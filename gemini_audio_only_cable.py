

import asyncio
import os
import sys
import traceback
import pyaudio
import json
import datetime
import canvas_ops
from google import genai
from dotenv import load_dotenv
import time
import socket
import threading
import warnings
# Import RAG functions from chroma_script
from chroma_db.chroma_script import rag_from_json
# Import canvas operations
from canvas_ops import get_canvas_item_id
load_dotenv()

# Suppress Gemini warnings about non-text parts
warnings.filterwarnings("ignore", message=".*non-text parts.*")
warnings.filterwarnings("ignore", message=".*inline_data.*")
warnings.filterwarnings("ignore", message=".*concatenated text result.*")
warnings.filterwarnings("ignore", category=UserWarning)

# Set global socket timeout for extended tool execution
socket.setdefaulttimeout(300)  # 5 minutes timeout
# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# Gemini configuration
MODEL = "models/gemini-2.0-flash-live-001"
CONFIG = {"response_modalities": ["AUDIO"]}

# System prompt for Gemini
SYSTEM_PROMPT = """
You are Medforce Agent — a professional clinical assistant integrated into a shared screen canvas system.
Your purpose is to assist users in analyzing and managing medical data for patient Sarah Miller (DILI case context).
All responses and actions must remain focused on this patient. YOU ONLY SPEAK ENGLISH.

You only communicate in **English**. Do not speak other language except english.

---

### PATIENT CONTEXT: SARAH MILLER (ALWAYS AVAILABLE IN YOUR MEMORY)

**Demographics:**
- Name: Sarah Miller
- Age: 53 years old
- Sex: Female
- MRN: MC-001001

**Primary Diagnosis:**
- Rheumatoid Arthritis (seropositive, active disease)

**Active Medical Problems:**
1. Rheumatoid arthritis (active, on treatment)
2. Essential hypertension (controlled on medication)
3. Mild chronic kidney disease (stable)
4. **CURRENT ACUTE ISSUE: Suspected drug-induced liver injury (DILI)**

**Current Medications:**
- Methotrexate 20mg weekly (started August 2015, dose increased September 2018)
- Folic Acid 5mg weekly (MTX supplementation)
- Lisinopril 10mg daily (for hypertension)
- Recent antibiotic: Trimethoprim-Sulfamethoxazole 800/160mg BID (June 15-25, 2025 for acute sinusitis)

**Known Allergies:**
- Penicillin (causes rash)

**Key Medical Timeline:**
- August 2015: RA diagnosis, started Methotrexate 10mg weekly
- September 2018: HTN diagnosed, MTX increased to 20mg, Lisinopril added
- March 2021: Mild CKD documented, stable
- June 15, 2025: Acute bacterial sinusitis, treated with TMP-SMX
- June 21, 2025: Emergency presentation with acute liver injury (jaundice, confusion, severe fatigue)

**Current Clinical Concern:**
Sarah Miller is experiencing suspected DILI from Methotrexate toxicity, potentially precipitated by TMP-SMX interaction during recent sinusitis treatment.

**HOW TO USE THIS CONTEXT:**
- For general questions about Sarah ("tell me about the patient", "what's her diagnosis"), use THIS summary - NO tool calls needed
- Only call `get_canvas_objects` when you need SPECIFIC detailed data NOT in this summary
- Examples:
  ✅ "What's Sarah's diagnosis?" → Answer directly: "Rheumatoid Arthritis"
  ✅ "How old is she?" → Answer directly: "53 years old"
  ❌ "Show me detailed lab trends" → Call get_canvas_objects
  ❌ "Navigate to biopsy results" → Call get_canvas_objects

---

### AUDIO COMMUNICATION RULES (CRITICAL - READ CAREFULLY)

**RULE 1: SPEAK NATURALLY - NO TECHNICAL JARGON**
- You are speaking AUDIO responses that humans will hear
- NEVER verbalize technical details like:
  ❌ "task id: task-123-456"
  ❌ "status: pending, executing, finished"
  ❌ "objectId: dashboard-item-xyz-123"
  ❌ JSON field names or database values
  ❌ System identifiers or technical codes

**RULE 2: WHAT TO SAY INSTEAD**
  ✅ "I've created a task to review the liver biopsy results"
  ✅ "I'm now showing you the patient summary"
  ✅ "The task is being processed"
  ✅ "I've navigated to the medications section"
  ✅ "Looking at the lab results now"

**RULE 3: BRIEF CONFIRMATIONS**
  After completing actions, give SHORT, natural confirmations:
  ✅ "Done. You can now see the lab results."
  ✅ "Task created successfully."
  ✅ "Navigating to the patient summary."
  ✅ "Here are the medication details."

**RULE 4: FORBIDDEN TO MENTION**
  - Database IDs (item-xxx, task-xxx, dashboard-item-xxx)
  - Status codes (pending, executing, finished) - say "in progress" or "completed" instead
  - Function names (navigate_canvas, generate_task, get_canvas_objects)
  - JSON structure, field names, or raw data
  - System implementation details
  - Object identifiers or technical references

**RULE 5: BE CONVERSATIONAL**
  - Speak as if you're a medical professional talking to a colleague
  - Use medical terminology appropriately but avoid tech-speak
  - Keep responses concise and relevant

---

### CORE BEHAVIOR RULES

1. **ANSWER MEDICAL QUESTIONS**
   - When the user asks about Sarah Miller's condition, diagnosis, lab results, or treatment:
     → **Call `get_canvas_objects`** with the query text to find relevant medical data on the canvas.
     → **Automatically navigate to the most relevant object** found in the results.
   - Use the returned information to provide a **complete, medically accurate** response.
   - Use all available EHR, lab, and historical data from canvas objects.
   - Never ask for clarification — always infer the most complete and reasonable medical answer.
   - Do not mention any technical identifiers (IDs, database names, etc.) in the response.
   - **Always navigate to relevant objects** to show the user the specific data being referenced.

2. **CANVAS OPERATIONS**
   - For any canvas-related user request (navigation, focusing, creating a to-do, etc.):
     → **First call `get_canvas_objects`** with a descriptive query to find the relevant object(s).
     → Then, use the returned objectId(s) to perform the next action:
       - For movement or focus: **`navigate_canvas`** with optional `subElement` for precise targeting
       - For creating a new task: **`generate_task`**
   - Never ask the user for object IDs — always resolve them via `get_canvas_objects`.
   - Use `subElement` parameter for precise navigation (e.g., "medications.methotrexate", "lab-results.alt").
   - When the action completes, briefly explain what was done (e.g., "Focused on the patient summary section.").

3. **TASK CREATION**
   - When the user asks to create a task ("create/make/add a task…"):
     → **First, ask for user confirmation** before creating the task.
     → Present the proposed task workflow details (title, description) to the user in short.
     → Wait for user approval before calling `generate_task`.
   - If user confirms, then call `get_canvas_objects` if needed (to identify context), then **`generate_task`**.
   - Populate structured fields:
       - `title`: short, clear summary of the workflow goal.
       - `description`: comprehensive description of the task workflow.
       - `todos`: array of main tasks with:
         - `id`: unique identifier for each task
         - `text`: task description
         - `status`: current status (pending, executing, finished)
         - `agent`: responsible agent for the task
         - `subTodos`: array of sub-tasks with text and status
   - **Always ask for confirmation before creating task workflows.**
   - After user confirms, explain that the task workflow was successfully created.


4. **LAB RESULTS**
   - When the user requests or discusses a lab parameter:
     → Use **`generate_lab_result`** with all relevant details.
   - If data is unavailable, generate a realistic result consistent with DILI context.

5. **SILENCE AND DISCIPLINE**
   - Remain silent unless:
     - The user directly asks a question, **or**
     - The user explicitly requests an action (navigate, create, get data, etc.).
   - Do not provide unsolicited commentary or background explanations.

6. **BACKGROUND PROCESSING**
   - When receiving messages starting with “BACKGROUND ANALYSIS COMPLETED:”, acknowledge and summarize results.
   - Do not restate the raw data; instead, provide a concise medical interpretation.

---

### FUNCTION USAGE SUMMARY

| User Intent | Function(s) to Call | Notes |
|--------------|--------------------|-------|
| Ask about Sarah Miller's condition or diagnosis | `get_canvas_objects` → `navigate_canvas` | Find relevant objects and navigate to them |
| Ask for lab result | `generate_lab_result` | Use realistic medical data if missing |
| Navigate / show specific data on canvas | `get_canvas_objects` → `navigate_canvas` | Find the relevant objectId first |
| Navigate to specific sub-element | `get_canvas_objects` → `navigate_canvas` with `subElement` | Use subElement for precise targeting |
| Create a to-do / task | Ask for confirmation → `get_canvas_objects` (if needed) → `generate_task` | Present task details, get approval, then create |
| Inspect available canvas items | `get_canvas_objects` | Return list or summary of items |

---

### RESPONSE GUIDELINES

- Always **call the actual tool** — never say “I will call a function”.
- Always **explain** what was accomplished after calling a function.
- Always use **get_canvas_objects** before any canvas operation requiring an objectId.
- Always **combine tool results with medical reasoning** in your explanations.
- Never display system details, IDs, or raw JSON responses to the user.
- Use precise medical terminology, but ensure clarity for clinicians.
- Stay concise, factual, and professional.

---

### TASK EXECUTION FLOW EXAMPLES (Conceptual)

**Question:**
> "What's the probable cause of Sarah Miller's elevated ALT levels?"

→ Call `get_canvas_objects(query="Probable cause of elevated ALT in Sarah Miller")`
→ Extract objectId from the most relevant result
→ Call `navigate_canvas(objectId=...)` to show the relevant data
→ Interpret response medically and explain.

**Navigation:**
> "Show me Sarah Miller's medication history on the canvas."

→ Call `get_canvas_objects(query="medication history")`
→ Extract `objectId` → Call `navigate_canvas(objectId=...)`
→ Confirm navigation to the user.

**Precise Navigation:**
> "Show me Sarah Miller's methotrexate medication specifically."

→ Call `get_canvas_objects(query="medications methotrexate")`
→ Extract `objectId` → Call `navigate_canvas(objectId="dashboard-item-medications-1234", subElement="medications.methotrexate")`
→ Confirm precise navigation to the user.

**Task:**
> "Create a task to review her latest liver biopsy results."

→ **First, ask for confirmation**: "I'd like to create a task workflow to review Sarah Miller's latest liver biopsy results. Here's what I propose:
   - Title: 'Liver Biopsy Analysis Workflow'
   - Description: 'Comprehensive analysis of liver biopsy results with detailed sub-tasks'
   - Todos: [
       {
         'id': 'task-101',
         'text': 'Initial Biopsy Review',
         'status': 'executing',
         'agent': 'Pathology Agent',
         'subTodos': [
           {'text': 'Examine tissue samples', 'status': 'finished'},
           {'text': 'Document histological findings', 'status': 'executing'},
           {'text': 'Compare with previous results', 'status': 'pending'}
         ]
       }
     ]
   
   Should I proceed with creating this task workflow?"

→ **Wait for user confirmation**

→ **If confirmed**: Call `get_canvas_objects(query="liver biopsy results")` if needed
→ Then call `generate_task(title="Liver Biopsy Analysis Workflow", description="Comprehensive analysis...", todos=[...])`
→ Confirm completion to the user. And say the task workflow will execute in the background by specialized agents.

---
"""



FUNCTION_DECLARATIONS = [
    {
        "name": "navigate_canvas",
        "description": "Navigate canvas to item with optional sub-element targeting for precise navigation",
        "parameters": {
            "type": "object",
            "properties": {
                "objectId": {
                    "type": "string",
                    "description": "Object id to navigate to (e.g., 'dashboard-item-patientcontext-1234')"
                },
                "subElement": {
                    "type": "string",
                    "description": "Optional sub-element within the object to focus on (e.g., 'medications.methotrexate', 'lab-results.alt', 'vitals.blood-pressure')"
                }
            },
            "required": ["objectId"]
        }
    },
    {
        "name": "generate_task",
        "description": "Generate a comprehensive task workflow with structured todos, sub-tasks, agents, and status tracking",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Main title of the task workflow"
                },
                "description": {
                    "type": "string",
                    "description": "Comprehensive description of the task workflow"
                },
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the task"
                            },
                            "text": {
                                "type": "string",
                                "description": "Task description"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "executing", "finished"],
                                "description": "Current status of the task"
                            },
                            "agent": {
                                "type": "string",
                                "description": "Agent responsible for executing this task"
                            },
                            "subTodos": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string",
                                            "description": "Sub-task description"
                                        },
                                        "status": {
                                            "type": "string",
                                            "enum": ["pending", "executing", "finished"],
                                            "description": "Status of the sub-task"
                                        }
                                    },
                                    "required": ["text", "status"]
                                },
                                "description": "Array of sub-tasks for this main task"
                            }
                        },
                        "required": ["id", "text", "status", "agent", "subTodos"]
                    },
                    "description": "Array of main tasks with their sub-tasks, agents, and status"
                }
            },
            "required": ["title", "description", "todos"]
        }
    },
    {
        "name": "generate_lab_result",
        "description": "Generate a lab result with value, unit, status, range, and trend information. If the data not available, generate it.",
        "parameters": {
            "type": "object",
            "properties": {
                "parameter": {
                    "type": "string",
                    "description": "Name of the medical parameter (e.g., Aspartate Aminotransferase) If not provided use the most relevant parameter"
                },
                "value": {
                    "type": "string",
                    "description": "The measured value of the parameter, generate it if not provided"
                },
                "unit": {
                    "type": "string",
                    "description": "Unit of measurement (e.g., U/L, mg/dL, etc.) generate it if not provided"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the parameter (optimal, warning, critical) generate it if not provided"
                },
                "range": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum normal value generate it if not provided"
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum normal value generate it if not provided"
                        },
                        "warningMin": {
                            "type": "number",
                            "description": "Minimum warning threshold generate it if not provided"
                        },
                        "warningMax": {
                            "type": "number",
                            "description": "Maximum warning threshold generate it if not provided"
                        }
                    },
                    "required": ["min", "max", "warningMin", "warningMax"],
                    "description": "Normal and warning ranges for the parameter"
                },
                "trend": {
                    "type": "string",
                    "description": "Trend direction (stable, increasing, decreasing, fluctuating) generate it if not provided"
                }
            },
            "required": ["parameter", "value", "unit", "status", "range", "trend"]
        }
    },
    {
        "name": "get_canvas_objects",
        "description": "Get canvas items details for canvas operations and answering questions",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to find specific canvas objectsId or items for answering questions or canvas operations"
                }
            },
            "required": ["query"]
        }
    }
]


CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": SYSTEM_PROMPT,
    "tools": [{"function_declarations": FUNCTION_DECLARATIONS}],
    "speech_config":{
        "voice_config": {"prebuilt_voice_config": {"voice_name": "Charon"}},
        "language_code": "en-GB"
    }
}
# Initialize PyAudio
pya = pyaudio.PyAudio()

class AudioOnlyGeminiCable:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.output_stream = None
        self.function_call_count = 0
        self.last_function_call_time = None
        
        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable not set!")
            sys.exit(1)
        
        # Configure client with extended timeout for tool execution
        self.client = genai.Client(
            http_options={
                "api_version": "v1beta",
                "timeout": 300  # 5 minutes timeout for tool execution
            }, 
            api_key=api_key
        )
        print(f"🔧 Gemini client initialized: {hasattr(self.client, 'aio')}")

    async def handle_tool_call(self, tool_call):
        """Handle tool calls from Gemini according to official documentation"""
        try:
            from google.genai import types
            
            # Track function calls
            self.function_call_count += 1
            self.last_function_call_time = datetime.datetime.now()
            
            print(f"🔧 Function Call #{self.function_call_count}")
            
            # Process each function call in the tool call
            function_responses = []
            for fc in tool_call.function_calls:
                function_name = fc.name
                arguments = fc.args
                
                print(f"  📋 {function_name}: {json.dumps(arguments, indent=2)[:100]}...")
                
                # Create action data for saving
                action_data = {
                    "function_name": function_name,
                    "arguments": arguments,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Save the function call to file (non-blocking)
                asyncio.create_task(self.save_function_call(arguments))
                
                # Create function response with actual canvas processing
                if fc.name == "get_canvas_objects":
                    query = arguments.get('query', '')
                    canvas_result = self.get_canvas_objects(query)
                    print("RAG Result Canvas:",canvas_result[:200])

                    fun_res = {
                        "result": {
                            "status": "Canvas objects retrieved",
                            "action": "Retrieved canvas items and will navigate to most relevant",
                            "query": query,
                            "canvas_data": canvas_result,
                            "message": f"I've retrieved relevant canvas objects for your query: '{query}'. I'll now navigate to the most relevant object to show you the specific data. Here's what I found: {canvas_result}",
                            "explanation": f"Canvas query '{query}' processed successfully. Retrieved relevant canvas items and will automatically navigate to the most relevant object."
                        }
                    }
                else:
                    fun_res = self.get_function_response(arguments)
                
                function_response = types.FunctionResponse(
                    id=fc.id,
                    name=fc.name,
                    response=fun_res
                )
                function_responses.append(function_response)
            
            # Send tool response back to Gemini
            await self.session.send_tool_response(function_responses=function_responses)
            print("  ✅ Response sent")
            
            # Add a delay to ensure the tool response is processed
            await asyncio.sleep(0.5)
            
            # Force session state reset by sending a simple message
            try:
                await self.session.send(input="Ready.")
                print("  🔄 Session reset")
            except Exception as reset_error:
                print(f"⚠️ Reset failed: {reset_error}")
            
        except Exception as e:
            print(f"❌ Function call error: {e}")
            # Send error response back to Gemini to clear the function call state
            try:
                from google.genai import types
                error_response = types.FunctionResponse(
                    id="error",
                    name="error",
                    response={"error": f"Function call failed: {str(e)}"}
                )
                await self.session.send_tool_response(function_responses=[error_response])
                print("  🔄 Error recovery completed")
            except Exception as error_send_error:
                print(f"❌ Error recovery failed: {error_send_error}")

    def get_function_response(self, arguments):
        if 'objectId' in arguments:
            object_id = arguments.get('objectId', '')
            sub_element = arguments.get('subElement', '')
            
            if sub_element:
                return { 
                    "result": {
                        "status": "Canvas navigation completed with sub-element focus",
                        "action": "Moved viewport to target object and focused on specific sub-element",
                        "objectId": object_id,
                        "subElement": sub_element,
                        "message": f"I've successfully navigated to the requested canvas object and focused on the specific sub-element '{sub_element}'. The viewport has been moved to show this precise information.",
                        "explanation": f"Navigation completed successfully to object '{object_id}' with focus on sub-element '{sub_element}'. The canvas view has been updated to show the specific requested data."
                    }
                }
            else:
                return { 
                    "result": {
                        "status": "Canvas navigation completed",
                        "action": "Moved viewport to target object",
                        "objectId": object_id,
                        "message": "I've successfully navigated to the requested canvas object. The viewport has been moved to focus on this item. You can now see the relevant information displayed on the canvas.",
                        "explanation": "Navigation completed successfully. The canvas view has been updated to show the requested object with all relevant details."
                    }
                }
        elif 'parameter' in arguments:
            return { 
                "result": {
                    "status": "Lab result generated",
                    "action": "Created lab result for medical parameter",
                    "parameter": arguments.get('parameter', 'Unknown'),
                    "value": arguments.get('value', 'N/A'),
                    "unit": arguments.get('unit', ''),
                    "status_level": arguments.get('status', 'Normal'),
                    "message": f"I've successfully generated a lab result for {arguments.get('parameter', 'the requested parameter')}: {arguments.get('value', 'N/A')} {arguments.get('unit', '')} (Status: {arguments.get('status', 'Normal')}). The result is now displayed on the canvas for your review.",
                    "explanation": f"Lab result created for {arguments.get('parameter', 'parameter')} with value {arguments.get('value', 'N/A')} {arguments.get('unit', '')}. Status: {arguments.get('status', 'Normal')}. The result has been added to the canvas for analysis."
                }
            }
        elif 'query' in arguments and len(arguments) == 1:
            # This is either query_chroma_collection or get_canvas_objects
            query = arguments.get('query', '')
            # We need to determine which function was called based on context
            # For now, we'll handle both cases and let the actual function call determine the response
            return {
                "result": {
                    "status": "Query processed",
                    "action": "Retrieved relevant information",
                    "query": query,
                    "message": f"I've processed your query: '{query}'. The relevant information has been retrieved and will be used to provide you with a comprehensive answer.",
                    "explanation": f"Query '{query}' has been processed successfully. The system has retrieved relevant information to answer your question."
                }
            }
        else:
            # For task creation, include the actual task details
            task_title = arguments.get('title', 'New Task')
            task_content = arguments.get('content', 'Task created')
            task_items = arguments.get('items', [])
            
            return {
                "result": {
                    "status": "Task created successfully",
                    "action": "Created task with detailed analysis",
                    "title": task_title,
                    "content": task_content,
                    "items": task_items,
                    "message": f"I've successfully created your confirmed task: '{task_title}'. {task_content}. The task includes {len(task_items)} step-by-step items. IMPORTANT: This task will be executed and analyzed by a Data Analyst Agent in the background. You'll receive detailed analysis results shortly.",
                    "explanation": f"Task '{task_title}' created with {len(task_items)} step-by-step items. Background execution initiated - Data Analyst Agent will process this task and provide comprehensive analysis.",
                    "executed_by": "Data Analyst Agent",
                    "execution_mode": "background",
                    "background_processing": "Data Analyst Agent will analyze the task and provide detailed results in the background"
                }
            }


    def get_canvas_objects(self, query):
        """Get canvas objects using RAG from JSON"""
        try:
            print(f"🔍 Getting canvas objects for query: {query}")
            result = rag_from_json("./chroma_db/boardItems.json", query, top_k=3)
            print(f"🔍 Canvas objects retrieved: {result[:200]}")
            return result if result else "No relevant canvas objects found for this query."
        except Exception as e:
            print(f"Error getting canvas objects: {e}")
            return f"Error retrieving canvas objects: {str(e)}"

    def start_background_agent_processing(self, action_data):
        """Start agent processing in background using threading (no asyncio.create_task)"""
        def run_agent_processing():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the agent processing
                loop.run_until_complete(self._handle_agent_processing(action_data))
                
            except Exception as e:
                print(f"❌ Error in background agent processing thread: {e}")
            finally:
                loop.close()
        
        # Start the background processing in a separate thread
        thread = threading.Thread(target=run_agent_processing, daemon=True)
        thread.start()
        print(f"  🔄 Background processing started")

    async def _handle_agent_processing(self, action_data):
        """Handle agent processing in background"""
        try:
            agent_res = await canvas_ops.get_agent_answer(action_data)
            await asyncio.sleep(2)
            create_agent_res = await canvas_ops.create_result(agent_res)
            print(f"  ✅ Analysis completed")
            
            
                
        except Exception as e:
            print(f"❌ Background processing error: {e}")
            # Send error info to Gemini
            error_message = f"BACKGROUND PROCESSING ERROR: The Data Analyst Agent encountered an error while processing your task: {str(e)}"
            try:
                await self.session.send(input=error_message)
                print(f"  📝 Error message sent to Gemini")
            except Exception as error_send_error:
                print(f"⚠️ Could not send error message: {error_send_error}")

    async def save_function_call(self, action_data):
        """Save the function call to a file"""
        if not action_data:
            return
        if 'objectId' in action_data:
            object_id = action_data["objectId"]
            sub_element = action_data.get("subElement", "")
            
            if sub_element:
                print(f"  🎯 Navigating to object {object_id} with sub-element focus: {sub_element}")
                # For now, we'll use the basic focus_item, but this could be enhanced
                # to support sub-element navigation in the future
                focus_res = await canvas_ops.focus_item(object_id,sub_element)
                print(f"  🎯 Navigation completed with sub-element focus: {sub_element}", focus_res)
            else:
                focus_res = await canvas_ops.focus_item(object_id)
                print(f"  🎯 Navigation completed", focus_res)
        elif 'parameter' in action_data:
            lab_res = await canvas_ops.create_lab(action_data)
            await asyncio.sleep(2)
            labId = lab_res['id']
            focus_res = await canvas_ops.focus_item(labId)
            print(f"  🧪 Lab result created")
        elif 'query' in action_data and len(action_data) == 1:
            # Handle canvas object queries with navigation
            query = action_data.get('query', '')
            print(f"  🔍 Canvas query processed: {query[:50]}...")
            
            # Get canvas objects and navigate to the most relevant one
            try:
                canvas_result = self.get_canvas_objects(query)
                print(f"  🔍 Canvas objects retrieved: {canvas_result[:100]}...")
                
                # Parse the result to extract objectId for navigation
                # The rag_from_json result should contain objectId information
                # For now, we'll trigger navigation after a short delay
                await asyncio.sleep(1)
                
                # Try to extract objectId from the canvas result
                # This is a simplified approach - in practice, you'd parse the JSON result
                print(f"  🎯 Will navigate to relevant object based on query results")
                
            except Exception as e:
                print(f"  ❌ Error processing canvas query: {e}")
        else:
            action_data['area'] = "planning-zone"
            with open("action_data.json", "w", encoding="utf-8") as f:
                json.dump(action_data, f, ensure_ascii=False, indent=4)
            task_res = await canvas_ops.create_todo(action_data)
            with open("action_data_response.json", "w", encoding="utf-8") as f:
                json.dump(task_res, f, ensure_ascii=False, indent=4)
            await asyncio.sleep(3)
            boxId = task_res['id']
            focus_res = await canvas_ops.focus_item(boxId)
            with open("action_data_focus.json", "w", encoding="utf-8") as f:
                json.dump(focus_res, f, ensure_ascii=False, indent=4)
            print(f"  📝 Task created")

            # Trigger agent processing in background
            self.start_background_agent_processing(action_data)
            


        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"function_call_object/gemini_function_call_{timestamp}.json"
            
            # with open(filename, 'w') as f:
            #     json.dump(action_data, f, indent=2)
            
            # print(f"💾 Function call saved to: {filename}")
            # print(f"📄 Content: {json.dumps(action_data, indent=2)}")
            
        except Exception as e:
            print(f"❌ Error saving function call: {e}")


    def find_input_device(self, substr: str) -> int:
        """Find input device by substring"""
        s = substr.lower()
        for i in range(pya.get_device_count()):
            info = pya.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0 and s in info['name'].lower():
                return i
        return None

    def find_output_device(self, substr: str) -> int:
        """Find output device by substring"""
        s = substr.lower()
        for i in range(pya.get_device_count()):
            info = pya.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0 and s in info['name'].lower():
                return i
        return None

    async def listen_audio(self):
        """Listen to CABLE Output (Google Meet audio) and send to Gemini"""
        print("🎤 Starting audio capture...")
        
        # Find CABLE Output device
        input_device_index = self.find_input_device("CABLE Output")
        if input_device_index is None:
            print("❌ CABLE Output device not found!")
            return
        
        input_info = pya.get_device_info_by_index(input_device_index)
        print(f"🎤 Using: {input_info['name']}")
        
        # Open audio stream
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=CHUNK_SIZE,
        )
        
        print("🎤 Audio ready!")
        
        # Read audio chunks and send to Gemini
        while True:
            try:
                data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False)
                await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
            except Exception as e:
                print(f"❌ Error reading audio: {e}")
                break

    async def receive_audio(self):
        """Receive audio responses from Gemini"""
        print("🔊 Starting response processing...")
        
        while True:
            try:
                turn = self.session.receive()
                async for response in turn:
                    # Handle audio data
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)
                        # Reduced logging - only log occasionally
                        # if self.function_call_count % 10 == 0:  # Log every 10th audio chunk
                        #     print(f"🔊 Audio: {len(data)} bytes")
                    
                    # Handle text responses (print them)
                    # if text := response.text:
                    #     print(f"💬 Gemini: {text}")
                        # Check if the text contains function call requests


                    # Enhanced function call detection with multiple methods
                    function_call_detected = False
                    
                    # Method 1: Check tool_call attribute
                    if hasattr(response, 'tool_call'):
                        if response.tool_call:
                            print("🔧 TOOL CALL DETECTED!")
                            await self.handle_tool_call(response.tool_call)
                            function_call_detected = True
 
                # Clear audio queue on turn completion to prevent overlap
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
                    
            except Exception as e:
                print(f"❌ Error receiving audio: {e}")
                break

    async def play_audio(self):
        """Play audio responses to CABLE Input (Google Meet will hear this)"""
        print("🔊 Setting up audio output...")
        
        # Find CABLE Input device
        output_device_index = self.find_output_device("Voicemeeter Input")
        if output_device_index is None:
            print("❌ Output device not found!")
            return
        
        output_info = pya.get_device_info_by_index(output_device_index)
        print(f"🔊 Using: {output_info['name']}")
        
        # Open output stream
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
            output_device_index=output_device_index,
        )
        
        print("🔊 Audio output ready!")
        
        # Play audio from queue with proper buffering
        while True:
            try:
                bytestream = await self.audio_in_queue.get()
                await asyncio.to_thread(stream.write, bytestream)
                # Add small delay to ensure proper audio streaming
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"❌ Error playing audio: {e}")
                break

    async def send_audio_to_gemini(self):
        """Send audio data to Gemini"""
        while True:
            try:
                audio_data = await self.out_queue.get()
                await self.session.send(input=audio_data)
            except Exception as e:
                print(f"❌ Error sending audio: {e}")
                break

    async def run(self):
        """Main function to run the audio-only Gemini session with CABLE devices"""
        print("🎵 Gemini Live API - Audio Only with CABLE Devices")
        print("=" * 60)
        print("🤖 LIVE MODE: Gemini AI is ENABLED")
        print("🎤 Capturing audio from Google Meet (CABLE Output)")
        print("🔊 Playing Gemini responses to Google Meet (CABLE Input)")
        print("=" * 60)
        print("📝 Instructions:")
        print("1. Start this script first")
        print("2. Then start visit_meet_with_audio.py in another terminal")
        print("3. Configure Google Meet audio settings:")
        print("   - Microphone: CABLE Output (VB-Audio Virtual Cable)")
        print("   - Speaker: CABLE Input (VB-Audio Virtual Cable)")
        print("4. Speak in the meeting - Gemini will respond with audio to the meeting")
        print("5. Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            # Connect to Gemini Live API
            # config = {
            #     "response_modalities": ["AUDIO"]
            # }
            
            async with (
                self.client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                
                # Create queues
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=10)
                
                print("🔗 Connected to Gemini Live API with system prompt")
                
                # Start all tasks
                tg.create_task(self.send_audio_to_gemini())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())
                
                # Keep running until interrupted
                try:
                    await asyncio.Event().wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down...")
                    raise asyncio.CancelledError("User requested exit")
                
        except asyncio.CancelledError:
            print("✅ Session ended")
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
        finally:
            # Clean up audio stream
            if self.audio_stream:
                self.audio_stream.close()
            print("🧹 Cleanup completed")

def main():
    """Main entry point"""
    # Suppress all warnings from the application
    warnings.filterwarnings("ignore")
    
    print("🎵 Gemini Live API - Audio Only with CABLE Devices")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key:")
        print("set GOOGLE_API_KEY=your_api_key_here")
        return
    
    gemini = AudioOnlyGeminiCable()
    asyncio.run(gemini.run())

# if __name__ == "__main__":
#     main()
main()
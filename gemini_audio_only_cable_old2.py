

import asyncio
import os
import sys
import traceback
import pyaudio
import json
import datetime
import canvas_ops
from google import genai
import time
import socket
import threading
import warnings
import inspect
import signal
import collections.abc

from chroma_db.chroma_script import rag_from_json, get_easl_answer_async
from dotenv import load_dotenv
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
# MODEL = "models/gemini-2.0-flash-live-001"
MODEL = "gemini-2.0-flash-live-001" # @param ["gemini-2.0-flash-live-001", "gemini-live-2.5-flash-preview","gemini-2.5-flash-preview-native-audio-dialog"] {"allow-input":true, isTemplate: true}
CONFIG = {"response_modalities": ["AUDIO"]}

# System prompt for Gemini
with open("system_prompt.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()



with open("system_function.json", "r", encoding="utf-8") as f:
    FUNCTION_DECLARATIONS = json.load(f)


CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": SYSTEM_PROMPT,
    # Only enable function_declarations - code_execution and google_search are NOT included
    # If Gemini tries to use them anyway, they will be handled gracefully in receive_audio
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
        self.tool_call_queue = None  # Queue for tool calls (following tutorial pattern)
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

    def _get_functions_dict(self):
        """Return dictionary mapping function names to their handler functions"""
        return {
            'get_canvas_objects': self._handle_get_canvas_objects,
            'navigate_canvas': self._handle_navigate_canvas,
            'generate_task': self._handle_generate_task,
            'generate_lab_result': self._handle_generate_lab_result,
            'query_chroma_collection': self._handle_query_chroma_collection,
            # Fallback for any other functions
            '_default': self._handle_default_function,
        }

    def _log_response_debug(self, response):
        """Log full response attributes for debugging/monitoring"""
        try:
            # Ensure log directory exists
            os.makedirs("log", exist_ok=True)

            # Prefer structured dump when available (handles binary by base64-encoding)
            payload_json = response.model_dump_json(exclude_none=True)

            # Quick on-console visibility
            print("🔍 Response dump (truncated):")
            # print(payload_json[:2000])
            attrs = [attr for attr in dir(response) if not attr.startswith('_')]

            print(f"🔍 Response attrs: {attrs}")

        except Exception as e:
            print(f"🔍 Could not dump response JSON: {e}")
            attrs = [attr for attr in dir(response) if not attr.startswith('_')]
            print(f"🔍 Response attrs: {attrs}")
            # Fallback to naive string representation
            payload_json = str(response)

        # Persist full response to file
        try:
            filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S_%f") + ".json"
            filepath = os.path.join("log", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(payload_json)
        except Exception as e:
            print(f"🔍 Could not write response log file: {e}")


    async def _run_tool_calls(self):
        """Process tool calls from queue in separate task (following tutorial pattern)"""
        functions = self._get_functions_dict()
        try:
            while True:
                tool_call = await self.tool_call_queue.get()
                await self._process_tool_call(tool_call, functions)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Error in tool call processing task: {e}")
            traceback.print_exc()

    async def _process_tool_call(self, tool_call, functions):
        """Process tool call following tutorial pattern with inspect.iscoroutine"""
        from google.genai import types
        
        # Track function calls
        self.function_call_count += 1
        self.last_function_call_time = datetime.datetime.now()
        
        print(f"🔧 Tool Call #{self.function_call_count}")
        
        for fc in tool_call.function_calls:
            function_name = fc.name
            arguments = fc.args
            
            print(f"  📋 Function: {function_name}")
            print(f"  📋 Arguments: {json.dumps(arguments, indent=2)[:200]}...")
            
            try:
                # Get the function handler (use default if not found)
                if function_name not in functions:
                    print(f"  ⚠️ Function {function_name} not found, using default handler")
                    fun = functions.get('_default', None)
                    if fun is None:
                        raise ValueError(f"Function {function_name} not found and no default handler available")
                else:
                    fun = functions[function_name]
                # Call the function with arguments
                called = fun(**arguments)
                
                # Check if it's a coroutine (async function)
                if inspect.iscoroutine(called):
                    print(f"  >> Starting {function_name}")
                    result = await called
                    print(f"  >> Done {function_name} >>> {repr(result)[:200]}...")
                    result = self._wrap_function_result(fc, result)
                    await self.session.send_tool_response(function_responses=[result])
                
                # Check if it's an AsyncIterable (streaming response)
                elif isinstance(called, collections.abc.AsyncIterable):
                    async for result in called:
                        result.will_continue = True
                        result = self._wrap_function_result(fc, result)
                        print(f"  >>> {repr(result)[:200]}...")
                        await self.session.send_tool_response(function_responses=[result])
                    
                    # Send final response with will_continue=False
                    result = self._wrap_function_result(
                        fc,
                        types.FunctionResponse(will_continue=False)
                    )
                    print(f"  >>> Final {repr(result)[:200]}...")
                    await self.session.send_tool_response(function_responses=[result])
                
                else:
                    raise TypeError(
                        f"expected {function_name} to return a coroutine or an "
                        f"AsyncIterable, got {type(called)}"
                    )
                    
            except Exception as e:
                print(f"  ❌ Error processing {function_name}: {e}")
                traceback.print_exc()
                # Send error response
                error_response = self._wrap_function_result(
                    fc,
                    {"error": str(e), "message": f"Error executing {function_name}: {str(e)}"}
                )
                await self.session.send_tool_response(function_responses=[error_response])

    def _wrap_function_result(self, fc, result):
        """Wrap function result into FunctionResponse (following tutorial pattern)"""
        from google.genai import types
        
        if result is None:
            return types.FunctionResponse(
                name=fc.name,
                id=fc.id,
                response={'result': 'ok'}
            )
        elif isinstance(result, types.FunctionResponse):
            result.name = fc.name
            result.id = fc.id
            return result
        else:
            # If result is already a dict with 'result' key, use it directly
            if isinstance(result, dict) and 'result' in result:
                return types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response=result
                )
            else:
                return types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response={'result': result}
                )

    def get_function_response(self, arguments):
        if 'objectId' in arguments:
            object_id = arguments.get('objectId', '')
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


    async def get_canvas_objects(self, query):
        """Get canvas objects using RAG from JSON"""
        try:
            print(f"🔍 Getting canvas objects for query: {query}")
            result = await rag_from_json(query, top_k=3)
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
            agent_res['zone'] = "raw-ehr-data-zone"
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

    def start_background_easl_processing(self, query):
        """Start agent processing in background using threading (no asyncio.create_task)"""
        def run_agent_processing():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the agent processing
                # loop.run_until_complete(self._handle_easl_processing(query))
                loop.run_until_complete(self._handle_easl_iframe(query))
                
            except Exception as e:
                print(f"❌ Error in background agent processing thread: {e}")
            finally:
                loop.close()
        
        # Start the background processing in a separate thread
        thread = threading.Thread(target=run_agent_processing, daemon=True)
        thread.start()
        print(f"  🔄 Background processing started")

    async def _handle_easl_processing(self, query):
        """Handle agent processing in background"""
        try:
            print("Start trigger EASL endpoint")
            try:
                question = await canvas_ops.get_agent_question(query)
                context = await canvas_ops.get_agent_context(query)
                easl_answer = await get_easl_answer_async(question=f"Question: {question}\n", context=context)
            except:
                easl_answer = {}
            await asyncio.sleep(2)
            easl_answer_str = ""
            

            if type(easl_answer) == dict:
                easl_answer_str += f"# Question\n{question}\n\n"
                easl_answer_str += f"# Context\n{context[:1000]}\n...truncated\n\n"
                easl_answer_str += f"# Short Answer\n{easl_answer.get('short_answer','')}\n\n"
                easl_answer_str += f"# Detailed Answer\n{easl_answer.get('detailed_answer','')}\n\n"
                easl_answer_str += f"# References\n"
                for r in easl_answer.get('guideline_references', []):
                    easl_answer_str += f"- {r.get('Source','')}\n"

            print(f"EASL Answer :\n{easl_answer_str[:200]}")
            result_data = {}
            result_data['title'] = "EASL Answer"
            result_data['content'] = easl_answer_str
            result_data['zone'] = "retrieved-data-zone"

            create_agent_res = await canvas_ops.create_result(result_data)
            print(f"  ✅ EASL Answer completed")
            
            # try:
            #     await self.session.send(input=easl_answer_str)
            #     print(f"  📝 Backround EASL result sent to Gemini")
            # except Exception as error_send_error:
            #     print(f"⚠️ Could not send error message: {error_send_error}")
            
                
        except Exception as e:
            traceback.print_exc()
            print(f"❌ Background EASL processing error: {e}")
            # Send error info to Gemini
            error_message = f"BACKGROUND EASL PROCESSING ERROR: EASL Agent encountered an error while processing your task: {str(e)}"
            try:
                await self.session.send(input=error_message)
                print(f"  📝 Error message sent to Gemini")
            except Exception as error_send_error:
                print(f"⚠️ Could not send error message: {error_send_error}")

    async def _handle_easl_iframe(self, query):
        """Handle agent processing in background"""
        try:
            print("Start trigger EASL endpoint")
            try:
                question = await canvas_ops.get_agent_question(query)
                # context = await canvas_ops.get_agent_context(query)
                easl_status = await canvas_ops.initiate_easl_iframe(question)
                print("iframe status:", easl_status)
            except:
                easl_status = {}
            await asyncio.sleep(2)


            iframe_id = "iframe-item-easl-interface"
            await canvas_ops.focus_item(iframe_id)
            print(f"  ✅ EASL Answer completed")
            
            # try:
            #     await self.session.send(input=easl_answer_str)
            #     print(f"  📝 Backround EASL result sent to Gemini")
            # except Exception as error_send_error:
            #     print(f"⚠️ Could not send error message: {error_send_error}")
            
                
        except Exception as e:
            traceback.print_exc()
            print(f"❌ Background EASL processing error: {e}")
            # Send error info to Gemini
            error_message = f"BACKGROUND EASL PROCESSING ERROR: EASL Agent encountered an error while processing your task: {str(e)}"
            try:
                await self.session.send(input=error_message)
                print(f"  📝 Error message sent to Gemini")
            except Exception as error_send_error:
                print(f"⚠️ Could not send error message: {error_send_error}")

    # Handler functions for each tool (following tutorial pattern)
    async def _handle_get_canvas_objects(self, query: str):
        """Handle get_canvas_objects function call"""
        canvas_result = await self.get_canvas_objects(query)
        print(f"  🔍 RAG Result Canvas: {canvas_result[:200]}...")
        
        # Execute navigation in background (non-blocking)
        asyncio.create_task(self.save_function_call_with_error_handling({'query': query}))
        
        return {
            "result": {
                "status": "Canvas objects retrieved",
                "action": "Retrieved canvas items and will navigate to most relevant",
                "query": query,
                "canvas_data": canvas_result,
                "message": f"I've retrieved relevant canvas objects for your query: '{query}'. I'll now navigate to the most relevant object to show you the specific data. Here's what I found: {canvas_result}",
                "explanation": f"Canvas query '{query}' processed successfully. Retrieved relevant canvas items and will automatically navigate to the most relevant object."
            }
        }

    async def _handle_navigate_canvas(self, objectId: str):
        """Handle navigate_canvas function call"""
        if not objectId:
            raise ValueError("objectId is required for navigate_canvas")
        
        focus_res = await canvas_ops.focus_item(objectId)
        print(f"  🎯 Navigation completed: {focus_res}")
        
        return {
            "result": {
                "status": "Canvas navigation completed",
                "action": "Moved viewport to target object",
                "objectId": objectId,
                "message": "I've successfully navigated to the requested canvas object. The viewport has been moved to focus on this item.",
                "explanation": "Navigation completed successfully."
            }
        }

    async def _handle_generate_task(self, **kwargs):
        """Handle generate_task function call"""
        # Execute in background and return immediate response
        asyncio.create_task(self.save_function_call_with_error_handling(kwargs))
        return self.get_function_response(kwargs)

    async def _handle_generate_lab_result(self, **kwargs):
        """Handle generate_lab_result function call"""
        # Execute in background and return immediate response
        asyncio.create_task(self.save_function_call_with_error_handling(kwargs))
        return self.get_function_response(kwargs)

    async def _handle_query_chroma_collection(self, query: str):
        """Handle query_chroma_collection function call"""
        # This would query your chroma collection
        # For now, execute in background and return immediate response
        asyncio.create_task(self.save_function_call_with_error_handling({'query': query}))
        return {
            "result": {
                "status": "Query processed",
                "action": "Retrieved relevant information from chroma collection",
                "query": query,
                "message": f"I've processed your query: '{query}'. The relevant information has been retrieved and will be used to provide you with a comprehensive answer.",
                "explanation": f"Query '{query}' has been processed successfully. The system has retrieved relevant information to answer your question."
            }
        }

    async def _handle_default_function(self, **kwargs):
        """Default handler for any function not explicitly defined"""
        # Execute in background and return immediate response
        asyncio.create_task(self.save_function_call_with_error_handling(kwargs))
        return self.get_function_response(kwargs)

    async def save_function_call_with_error_handling(self, action_data):
        """Execute function call locally with proper error handling and reporting"""
        try:
            await self.save_function_call(action_data)
        except Exception as e:
            print(f"  ❌ Error in save_function_call_with_error_handling: {e}")
            traceback.print_exc()
            # Report error back to Gemini
            try:
                error_msg = f"Error executing function call: {str(e)}"
                await self.session.send(input=error_msg)
                print(f"  📝 Error reported to Gemini")
            except Exception as send_error:
                print(f"  ⚠️ Could not send error to Gemini: {send_error}")

    async def save_function_call(self, action_data):
        """Execute function call locally (canvas operations, etc.)"""
        if not action_data:
            return
        
        try:
            if 'objectId' in action_data:
                object_id = action_data["objectId"]
                focus_res = await canvas_ops.focus_item(object_id)
                print(f"  🎯 Navigation completed: {focus_res}")
            elif 'parameter' in action_data:
                lab_res = await canvas_ops.create_lab(action_data)
                await asyncio.sleep(2)
                labId = lab_res['id']
                focus_res = await canvas_ops.focus_item(labId)
                print(f"  🧪 Lab result created: {labId}")
            elif 'query' in action_data and len(action_data) == 1:
                # Handle canvas object queries with navigation
                query = action_data.get('query', '')
                print(f"  🔍 Canvas query processed: {query[:50]}...")
                
                # Get canvas objects and navigate to the most relevant one
                try:
                    canvas_result = await self.get_canvas_objects(query)
                    print(f"  🔍 Canvas objects retrieved: {canvas_result[:100]}...")
                    await asyncio.sleep(1)
                    print(f"  🎯 Will navigate to relevant object based on query results")
                except Exception as e:
                    print(f"  ❌ Error processing canvas query: {e}")
                    # Report error back to Gemini
                    try:
                        error_msg = f"Error processing canvas query '{query}': {str(e)}"
                        await self.session.send(input=error_msg)
                    except:
                        pass
            elif "question" in action_data:
                print(f"  🔍 Start EASL Processing:\n {action_data}...")

                query = action_data.get('question', '')
                easl_todo_payload = {
                    "title": "EASL Guideline Query Workflow",
                    "description": "Handling query to EASL Guideline Agent in background",
                    "todos": [
                        {
                        "id": "task-101",
                        "text": "Creating question query and generating context",
                        "status": "finished",
                        "agent": "Data Analyst Agent",
                        "subTodos": [
                                {
                                "text": f"Base question : {query}",
                                "status": "finished"
                                },
                                {
                                "text": "Detailed Question is generated by ContextGen Agent",
                                "status": "pending"
                                }
                            ]
                        },
                        {
                        "id": "task-101",
                        "text": "Send query to EASL Guideline Agent",
                        "status": "finished",
                        "agent": "Data Analyst Agent",
                        "subTodos": [
                                {
                                "text": f"Query is processing",
                                "status": "finished"
                                },
                                {
                                "text": "Result is created in canvas",
                                "status": "pending"
                                }
                            ]
                        }
                    ]
                    }
                task_res = await canvas_ops.create_todo(easl_todo_payload)
                await asyncio.sleep(3)
                self.start_background_easl_processing(query)
                print(f"  🔍 EASL question processed: {query[:50]}...")
            
            else:
                action_data['area'] = "planning-zone"

                task_res = await canvas_ops.create_todo(action_data)

                await asyncio.sleep(3)
                boxId = task_res['id']
                focus_res = await canvas_ops.focus_item(boxId)

                print(f"  📝 Task created")
                await asyncio.sleep(3)

                # Trigger agent processing in background
                self.start_background_agent_processing(action_data)
        except Exception as e:
            print(f"  ❌ Error in save_function_call: {e}")
            traceback.print_exc()
            # Re-raise to be caught by save_function_call_with_error_handling
            raise

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
        """Receive audio responses from Gemini - only handles audio/text, tools go to separate task"""
        print("🔊 Starting response processing...")
        
        while True:
            with open("agent_status.json", "r", encoding="utf-8") as f:
                agent_status = json.load(f)
            if not agent_status.get('mute'):
                try:
                    turn = self.session.receive()
                    async for response in turn:
                        # self._log_response_debug(response)
                        # Handle text parts
                        if (response.server_content and 
                            response.server_content.model_turn and 
                            response.server_content.model_turn.parts and 
                            hasattr(response.server_content.model_turn.parts[0], 'text')):
                            if text := response.server_content.model_turn.parts[0].text:
                                print(f"📝 Text response: {text[:100]}...")
                                continue

                        # Handle audio data parts
                        if (response.server_content and 
                            response.server_content.model_turn and 
                            response.server_content.model_turn.parts and 
                            hasattr(response.server_content.model_turn.parts[0], 'data')):
                            if data := response.server_content.model_turn.parts[0].data:
                                self.audio_in_queue.put_nowait(data)
                                continue

                        # Handle direct audio data (for live streaming)
                        if hasattr(response, 'data') and response.data:
                            self.audio_in_queue.put_nowait(response.data)
                            continue

                        # Handle server_content with executable_code/code_execution_result (ignore but log to avoid warnings)
                        server_content = response.server_content
                        if server_content and server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                if hasattr(part, 'executable_code') and part.executable_code:
                                    print(f"  ⚠️ Ignoring executable_code (code execution disabled)")
                                if hasattr(part, 'code_execution_result') and part.code_execution_result:
                                    print(f"  ⚠️ Ignoring code_execution_result (code execution disabled)")

                        # Queue tool_call for async processing
                        tool_call = response.tool_call
                        if tool_call is not None:
                            print("🔧 Tool call detected - queuing for processing")
                            await self.tool_call_queue.put(tool_call)
                            continue
    
                    # Clear audio queue on turn completion to prevent overlap
                    while not self.audio_in_queue.empty():
                        self.audio_in_queue.get_nowait()
                        
                except Exception as e:
                    print(f"❌ Error receiving audio: {e}")
                    traceback.print_exc()
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
        agent_status = {
            "mute" : False
        }
        with open("agent_status.json", "w", encoding="utf-8") as f:
            json.dump(agent_status, f,indent=4)
        try:

            async with (
                self.client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session


                
                # Create queues
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=10)
                self.tool_call_queue = asyncio.Queue()  # Queue for tool calls
                
                print("🔗 Connected to Gemini Live API with system prompt")
                
                # Start all tasks (following tutorial pattern with separate tool call task)
                tg.create_task(self.send_audio_to_gemini())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())
                tg.create_task(self._run_tool_calls())  # Separate task for tool call processing
                
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
    
    # Set up a handler for the SIGTERM signal to ensure graceful shutdown
    def sigterm_handler(_signo, _stack_frame):
        # Raise KeyboardInterrupt to trigger the existing graceful shutdown logic
        print("\n🛑 SIGTERM received, shutting down gracefully...")
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, sigterm_handler)
    except (ValueError, AttributeError) as e:
        # signal handling might not be available in all environments (e.g., non-main threads on Windows)
        print(f"⚠️ Could not set SIGTERM handler: {e}. Graceful shutdown via terminate signal may not work.")

    gemini = AudioOnlyGeminiCable()
    asyncio.run(gemini.run())

# if __name__ == "__main__":
#     main()
main()
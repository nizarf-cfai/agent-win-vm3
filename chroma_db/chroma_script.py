
# import os, json, requests
# import chromadb
# from chromadb.config import Settings
# from typing import List
# import google.generativeai as genai
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from dotenv import load_dotenv
# load_dotenv()

# BASE_URL = "https://board-v2-ten.vercel.app"

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_board_items():
#     """Fetch board items from Vercel API with timeout and error handling"""
#     url = BASE_URL + "/api/board-items"
#     try:
#         print(f"🔍 Fetching board items from: {url}")
#         response = requests.get(url, timeout=10)  # Add 10 second timeout
#         response.raise_for_status()  # Raise exception for bad status codes (4xx, 5xx)
#         data = response.json()
#         print(f"✅ Successfully fetched {len(data)} board items")
#         return data
#     except requests.exceptions.Timeout:
#         print(f"❌ Timeout: Board items API took longer than 10 seconds")
#         return []
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Network error fetching board items: {e}")
#         return []
#     except Exception as e:
#         print(f"❌ Unexpected error fetching board items: {e}")
#         return []

# def start_easl(question: str):
#     print(f"Starting EASL for question: {question}")
#     url = "https://inference-dili-16771232505.us-central1.run.app/generate-answers"

#     data = {
#         "questions": [
#             {
#                 "question": question,
#                 "question_id": "q1"
#             }
#         ],
#         "model_type": "reasoning_model"
#     }

#     response = requests.post(url, json=data)
#     return response

# def get_easl_answer(question: str):
#     answer = ""
#     init_response = start_easl(question)
#     print(f"Initial response: {init_response.status_code}")
#     if init_response.status_code == 200:
#         task_id = init_response.text.replace('"','')
#         print(f"Task ID: {task_id}")
#         retries = 0
#         while True:
#             print(f"Checking status of EASL. Retries: {retries}")
#             status_response = requests.get(f"https://inference-dili-16771232505.us-central1.run.app/generate-answers/status/{task_id}")
#             print(f"Status response: {status_response.status_code}")
#             if status_response.status_code == 200:
#                 status_data = status_response.json()
#                 print(f"Status data: {status_data}")
#                 if status_data['status'] == 'completed':
#                     print(f"EASL completed. Getting result.")
#                     result_response = requests.get(f"https://inference-dili-16771232505.us-central1.run.app/generate-answers/result/{task_id}")
#                     result_data = result_response.json()
#                     answer = result_data['results'][0]['llm_answer']
#                     break
#             time.sleep(3)
#             retries += 1
#             if retries > 5:
#                 break
#     return answer


# # ----------------------------
# # Common embedding helper
# # ----------------------------
# def embed_texts(texts: List[str]) -> List[List[float]]:
#     """Embed texts using Gemini embedding model"""
#     model = "models/text-embedding-004"
#     try:
#         res = genai.embed_content(model=model, content=texts)
        
        
#         # Handle the response structure correctly
#         if "embedding" in res:
#             # Single text input - but we might have multiple chunks
#             embedding = res["embedding"]
#             # If it's a list of lists (multiple embeddings), return as is
#             if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
#                 return embedding
#             # If it's a single embedding (list of floats), wrap it
#             else:
#                 return [embedding]
#         elif "data" in res:
#             # Multiple text inputs
#             embeddings = [d["embedding"] for d in res["data"]]
#             return embeddings
#         else:
#             # Fallback - try to extract embeddings from the response
#             print(f"Unexpected response structure: {list(res.keys())}")
#             return []
#     except Exception as e:
#         print(f"Error in embed_texts: {e}")
#         return []

# # ----------------------------
# # 1️⃣ Build Chroma from text files
# # ----------------------------
# def build_chroma_from_texts(dir_path: str, persist_dir: str = "./chroma_store"):
#     """Load text files, chunk, and store in Chroma vector DB"""
#     client = chromadb.PersistentClient(path=persist_dir)
#     collection = client.get_or_create_collection(name="local_docs")

#     splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

#     for fname in os.listdir(dir_path):
#         if not fname.endswith(".txt"):
#             continue
#         fpath = os.path.join(dir_path, fname)
#         with open(fpath, "r", encoding="utf-8") as f:
#             text = f.read()

#         chunks = splitter.split_text(text)
#         embeddings = embed_texts(chunks)
#         ids = [f"{fname}_{i}" for i in range(len(chunks))]

#         collection.add(documents=chunks, embeddings=embeddings, ids=ids)
#         # print(f"Stored {len(chunks)} chunks from {fname}")

#     # print("✅ Chroma built successfully.")
#     return collection


# # ----------------------------
# # 1.5️⃣ Query from persistent ChromaDB collection
# # ----------------------------
# def query_chroma_collection(query: str, persist_dir: str = "./chroma_store", collection_name: str = "local_docs", top_k: int = 3):

#     try:
#         # Connect to the persistent ChromaDB
#         client = chromadb.PersistentClient(path=persist_dir)
#         collection = client.get_collection(name=collection_name)
        
#         # Create custom embedding function for queries
#         class CustomEmbeddingFunction:
#             def __call__(self, input):
#                 return embed_texts(input)
            
#             def embed_query(self, input, **kwargs):
#                 embeddings = embed_texts([input])
#                 result = embeddings[0] if embeddings else []
#                 return [result]
        
#         # Set the embedding function for the collection
#         collection._embedding_function = CustomEmbeddingFunction()
        
#         # Perform the query
#         results = collection.query(
#             query_texts=[query],
#             n_results=top_k
#         )
        
#         # Extract and return the documents
#         if results["documents"] and results["documents"][0]:
#             context = "\n".join(results["documents"][0])
#             easl_question = f"Question: {query}\nContext: {context}"
#             easl_answer = get_easl_answer(easl_question)

#             rag_res = f"RAG Result: {context}\nEASL Answer: {easl_answer}"

#             return rag_res
#         else:
#             return []
            
#     except Exception as e:
#         print(f"Error querying ChromaDB collection: {e}")
#         return []


# # ----------------------------
# # 2️⃣ RAG from JSON file (no DB)
# # ----------------------------
# # ---------- Helper: JSON → Markdown ----------
# # def json_to_markdown(obj: dict, index: int = 0) -> str:
# #     """
# #     Convert one JSON object into flat Markdown text.
# #     - Only a single '# Record {index}' heading.
# #     - No nested or secondary headings.
# #     - Nested dicts/lists flattened into simple key paths.
# #     """
# #     lines = [f"# Object Record {index + 1}"]

# def json_to_markdown(obj: dict, index: int = 0) -> str:
#     """
#     Convert one JSON object into flat Markdown text.
#     Enhanced with RAG-optimized metadata for better search relevance.
#     """
#     lines = [f"# Object Record {index + 1}"]
    
#     # Add RAG optimization metadata for summary items
#     component_type = obj.get('componentType', '')
#     item_type = obj.get('type', '')
    
#     # Boost summary/overview components with extra searchable keywords
#     if component_type == 'PatientContext':
#         lines.append("**SUMMARY ITEM - HIGH PRIORITY**")
#         lines.append("**Search Keywords:** patient summary, patient overview, patient context, sarah miller overview, demographics, primary diagnosis, patient profile, medical summary, patient snapshot, quick view, patient information, about patient")
#         lines.append("**Item Type:** PRIMARY PATIENT SUMMARY")
#     elif component_type == 'AdverseEventAnalytics':
#         lines.append("**SUMMARY ITEM - HIGH PRIORITY**")
#         lines.append("**Search Keywords:** adverse events summary, DILI summary, liver injury overview, event analysis, safety summary, adverse reactions overview")
#         lines.append("**Item Type:** ADVERSE EVENT SUMMARY")
#     elif component_type == 'EncounterTimeline':
#         lines.append("**DETAILED DATA ITEM**")
#         lines.append("**Search Keywords:** detailed timeline, full encounter history, complete medical history")
#         lines.append("**Item Type:** DETAILED ENCOUNTER DATA")
#     elif component_type == 'DifferentialDiagnosis':
#         lines.append("**DETAILED DATA ITEM**")
#         lines.append("**Search Keywords:** detailed differential, complete diagnosis list, full diagnostic analysis")
#         lines.append("**Item Type:** DETAILED DIAGNOSTIC DATA")


#     def flatten(prefix, value):
#         if isinstance(value, dict):
#             for k, v in value.items():
#                 new_key = f"{prefix}_{k}" if prefix else k
#                 flatten(new_key, v)
#         elif isinstance(value, list):
#             for i, v in enumerate(value):
#                 new_key = f"{prefix}_{i}" if prefix else f"{prefix}_{i}"
#                 flatten(new_key, v)
#         else:
#             key_clean = prefix.replace("_", " ")
#             if key_clean == 'id':
#                 key_clean = 'objectId'
#             lines.append(f"**{key_clean}:** {value}")

#     flatten("", obj)
#     return "\n".join(lines)


# # ---------- Main Function ----------
# def rag_from_json(json_path: str="", query: str="", top_k: int = 3):
#     """
#     Load JSON (list of objects), convert each record to Markdown,
#     embed chunks in memory, and perform semantic RAG search.
#     """
#     import hashlib
#     import time
    
#     # Create in-memory Chroma collection with custom embedding function
#     client = chromadb.Client(Settings(anonymized_telemetry=False))
    
#     # Create a unique collection name based on JSON path and timestamp
#     json_hash = hashlib.md5(json_path.encode()).hexdigest()[:8]
#     timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp
#     collection_name = f"temp_json_rag_{json_hash}_{timestamp}"
    
#     try:
#         # Create a custom embedding function for queries
#         class CustomEmbeddingFunction:
#             def __call__(self, input):
#                 return embed_texts(input)
            
#             def embed_query(self, input, **kwargs):
#                 embeddings = embed_texts([input])
#                 result = embeddings[0] if embeddings else []
#                 # ChromaDB expects a list of lists even for single query
#                 return [result]
        
#         # Try to delete existing collection if it exists, then create new one
#         try:
#             client.delete_collection(name=collection_name)
#         except:
#             pass  # Collection doesn't exist, which is fine
        
#         collection = client.create_collection(
#             name=collection_name,
#             embedding_function=CustomEmbeddingFunction()
#         )

#         # Load JSON data
#         # with open(json_path, "r", encoding="utf-8") as f:
#         #     data = json.load(f)
#         data = get_board_items()

#         # Normalize: list of dicts
#         if isinstance(data, dict):
#             data = [data]

#         # Convert each object to Markdown string
#         md_blocks = [json_to_markdown(obj) for obj in data]

#         # Chunk each Markdown block
#         # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         # chunks = []
#         # for block in md_blocks:
#         #     chunks.extend(splitter.split_text(block))
#         chunks = md_blocks
#         # Embed and store in Chroma
#         embeddings = embed_texts(chunks)
#         ids = [f"chunk_{i}" for i in range(len(chunks))]
        
#         # Suppress any output from ChromaDB by redirecting stdout and stderr
#         import sys
#         import os
#         from contextlib import redirect_stdout, redirect_stderr
        
#         # Save original stdout and stderr
#         original_stdout = sys.stdout
#         original_stderr = sys.stderr
        
#         # Redirect to devnull
#         with open(os.devnull, 'w') as devnull:
#             sys.stdout = devnull
#             sys.stderr = devnull
#             try:
#                 collection.add(documents=chunks, embeddings=embeddings, ids=ids)
#             finally:
#                 # Restore original stdout and stderr
#                 sys.stdout = original_stdout
#                 sys.stderr = original_stderr

#         # Query
#         results = collection.query(query_texts=[query], n_results=top_k)
#         context = "\n".join(results["documents"][0])
        
#         # TEMPORARY FIX: Disable EASL to prevent timeout errors
#         # TODO: Re-enable EASL once connectivity issues are resolved
#         # easl_question = f"Question: {query}\nContext: {context}"
#         # easl_answer = get_easl_answer(easl_question)
#         # rag_res = f"RAG Result: {context}\nEASL Answer: {easl_answer}"
        
#         # Return RAG results only for now (more reliable)
#         return context
        
#     finally:
#         # Clean up: delete the temporary collection
#         try:
#             client.delete_collection(name=collection_name)
#         except:
#             pass  # Collection might already be deleted, which is fine



# ## RUN THIS FOR FIRST TIME TO CREATE VECTOR STORE
# # collection = build_chroma_from_texts("patient_data", "./chroma_store")
# # print("✅ Collection built successfully!")
    

########################new

import os, json, requests
import chromadb
from chromadb.config import Settings
from typing import List
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import time
load_dotenv()

BASE_URL = "https://board-v2-ten.vercel.app"

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# EASL Configuration with aggressive timeouts
EASL_ENABLED = True  # Can be toggled via environment variable
EASL_INITIAL_TIMEOUT = 15  # Timeout for initial EASL request (seconds)
EASL_STATUS_TIMEOUT = 5    # Timeout for status check requests (seconds)
EASL_MAX_RETRIES = 3       # Maximum number of status check retries
EASL_RETRY_DELAY = 2       # Delay between retries (seconds)
EASL_TOTAL_TIMEOUT = 30    # Total time limit for entire EASL operation (seconds)

def get_board_items():
    """Fetch board items from Vercel API with timeout and error handling"""
    url = BASE_URL + "/api/board-items"
    try:
        print(f"🔍 Fetching board items from: {url}")
        response = requests.get(url, timeout=10)  # Add 10 second timeout
        response.raise_for_status()  # Raise exception for bad status codes (4xx, 5xx)
        data = response.json()
        print(f"✅ Successfully fetched {len(data)} board items")
        return data
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Board items API took longer than 10 seconds")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching board items: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching board items: {e}")
        return []

def start_easl(question: str):
    """Start EASL processing with timeout protection"""
    print(f"🚀 Starting EASL for question: {question}")
    url = "https://inference-dili-16771232505.us-central1.run.app/generate-answers"

    data = {
        "questions": [
            {
                "question": question,
                "question_id": "q1"
            }
        ],
        "model_type": "reasoning_model"
    }

    try:
        response = requests.post(url, json=data, timeout=EASL_INITIAL_TIMEOUT)
        print(f"✅ EASL initial response: {response.status_code}")
        return response
    except requests.exceptions.Timeout:
        print(f"⏱️ EASL initial request timed out after {EASL_INITIAL_TIMEOUT}s")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ EASL request error: {e}")
        raise

def get_easl_answer(question: str):
    """
    Get EASL answer with comprehensive timeout protection and fallback.
    Returns empty string if EASL fails or times out - caller should handle gracefully.
    """
    answer = ""
    start_time = time.time()
    
    try:
        # Check if EASL is enabled
        if not EASL_ENABLED:
            print("ℹ️ EASL is disabled, skipping")
            return ""
        
        # Initial EASL request
        init_response = start_easl(question)
        
        if init_response.status_code != 200:
            print(f"⚠️ EASL initial request failed with status: {init_response.status_code}")
            return ""
        
        task_id = init_response.text.replace('"', '')
        print(f"📋 EASL Task ID: {task_id}")
        
        retries = 0
        while retries < EASL_MAX_RETRIES:
            # Check total timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > EASL_TOTAL_TIMEOUT:
                print(f"⏱️ EASL total timeout exceeded ({EASL_TOTAL_TIMEOUT}s), aborting")
                return ""
            
            print(f"🔍 Checking EASL status (attempt {retries + 1}/{EASL_MAX_RETRIES})")
            
            try:
                status_response = requests.get(
                    f"https://inference-dili-16771232505.us-central1.run.app/generate-answers/status/{task_id}",
                    timeout=EASL_STATUS_TIMEOUT
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 EASL status: {status_data.get('status', 'unknown')}")
                    
                    if status_data.get('status') == 'completed':
                        print(f"✅ EASL completed, retrieving result")
                        result_response = requests.get(
                            f"https://inference-dili-16771232505.us-central1.run.app/generate-answers/result/{task_id}",
                            timeout=EASL_STATUS_TIMEOUT
                        )
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            answer = result_data.get('results', [{}])[0].get('llm_answer', '')
                            print(f"✅ EASL answer retrieved: {len(answer)} characters")
                            break
                        else:
                            print(f"⚠️ EASL result request failed: {result_response.status_code}")
                            return ""
                    elif status_data.get('status') == 'failed':
                        print(f"❌ EASL processing failed")
                        return ""
                else:
                    print(f"⚠️ EASL status check failed: {status_response.status_code}")
                
            except requests.exceptions.Timeout:
                print(f"⏱️ EASL status check timed out")
            except requests.exceptions.RequestException as e:
                print(f"❌ EASL status check error: {e}")
            
            # Wait before next retry
            time.sleep(EASL_RETRY_DELAY)
            retries += 1
        
        if not answer and retries >= EASL_MAX_RETRIES:
            print(f"⚠️ EASL max retries reached, no answer retrieved")
        
    except requests.exceptions.Timeout:
        print(f"⏱️ EASL timed out, returning empty answer")
    except Exception as e:
        print(f"❌ EASL error: {e}")
    
    return answer


# ----------------------------
# Common embedding helper
# ----------------------------
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed texts using Gemini embedding model"""
    model = "models/text-embedding-004"
    try:
        res = genai.embed_content(model=model, content=texts)
        
        
        # Handle the response structure correctly
        if "embedding" in res:
            # Single text input - but we might have multiple chunks
            embedding = res["embedding"]
            # If it's a list of lists (multiple embeddings), return as is
            if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                return embedding
            # If it's a single embedding (list of floats), wrap it
            else:
                return [embedding]
        elif "data" in res:
            # Multiple text inputs
            embeddings = [d["embedding"] for d in res["data"]]
            return embeddings
        else:
            # Fallback - try to extract embeddings from the response
            print(f"Unexpected response structure: {list(res.keys())}")
            return []
    except Exception as e:
        print(f"Error in embed_texts: {e}")
        return []

# ----------------------------
# 1️⃣ Build Chroma from text files
# ----------------------------
def build_chroma_from_texts(dir_path: str, persist_dir: str = "./chroma_store"):
    """Load text files, chunk, and store in Chroma vector DB"""
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="local_docs")

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

    for fname in os.listdir(dir_path):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(dir_path, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)
        embeddings = embed_texts(chunks)
        ids = [f"{fname}_{i}" for i in range(len(chunks))]

        collection.add(documents=chunks, embeddings=embeddings, ids=ids)
        # print(f"Stored {len(chunks)} chunks from {fname}")

    # print("✅ Chroma built successfully.")
    return collection


# ----------------------------
# 1.5️⃣ Query from persistent ChromaDB collection
# ----------------------------
def query_chroma_collection(query: str, persist_dir: str = "./chroma_store", collection_name: str = "local_docs", top_k: int = 3):

    try:
        # Connect to the persistent ChromaDB
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_collection(name=collection_name)
        
        # Create custom embedding function for queries
        class CustomEmbeddingFunction:
            def __call__(self, input):
                return embed_texts(input)
            
            def embed_query(self, input, **kwargs):
                embeddings = embed_texts([input])
                result = embeddings[0] if embeddings else []
                return [result]
        
        # Set the embedding function for the collection
        collection._embedding_function = CustomEmbeddingFunction()
        
        # Perform the query
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Extract and return the documents
        if results["documents"] and results["documents"][0]:
            context = "\n".join(results["documents"][0])
            easl_question = f"Question: {query}\nContext: {context}"
            easl_answer = get_easl_answer(easl_question)

            rag_res = f"RAG Result: {context}\nEASL Answer: {easl_answer}"

            return rag_res
        else:
            return []
            
    except Exception as e:
        print(f"Error querying ChromaDB collection: {e}")
        return []


# ----------------------------
# 2️⃣ RAG from JSON file (no DB)
# ----------------------------
# ---------- Helper: JSON → Markdown ----------
# def json_to_markdown(obj: dict, index: int = 0) -> str:
#     """
#     Convert one JSON object into flat Markdown text.
#     - Only a single '# Record {index}' heading.
#     - No nested or secondary headings.
#     - Nested dicts/lists flattened into simple key paths.
#     """
#     lines = [f"# Object Record {index + 1}"]

def json_to_markdown(obj: dict, index: int = 0) -> str:
    """
    Convert one JSON object into flat Markdown text.
    Enhanced with RAG-optimized metadata for better search relevance.
    """
    lines = [f"# Object Record {index + 1}"]
    
    # Add RAG optimization metadata for summary items
    component_type = obj.get('componentType', '')
    item_type = obj.get('type', '')
    
    # Boost summary/overview components with extra searchable keywords
    if component_type == 'PatientContext':
        lines.append("**SUMMARY ITEM - HIGH PRIORITY**")
        lines.append("**Search Keywords:** patient summary, patient overview, patient context, sarah miller overview, demographics, primary diagnosis, patient profile, medical summary, patient snapshot, quick view, patient information, about patient")
        lines.append("**Item Type:** PRIMARY PATIENT SUMMARY")
    elif component_type == 'AdverseEventAnalytics':
        lines.append("**SUMMARY ITEM - HIGH PRIORITY**")
        lines.append("**Search Keywords:** adverse events summary, DILI summary, liver injury overview, event analysis, safety summary, adverse reactions overview")
        lines.append("**Item Type:** ADVERSE EVENT SUMMARY")
    elif component_type == 'EncounterTimeline':
        lines.append("**DETAILED DATA ITEM**")
        lines.append("**Search Keywords:** detailed timeline, full encounter history, complete medical history")
        lines.append("**Item Type:** DETAILED ENCOUNTER DATA")
    elif component_type == 'DifferentialDiagnosis':
        lines.append("**DETAILED DATA ITEM**")
        lines.append("**Search Keywords:** detailed differential, complete diagnosis list, full diagnostic analysis")
        lines.append("**Item Type:** DETAILED DIAGNOSTIC DATA")


    def flatten(prefix, value):
        if isinstance(value, dict):
            for k, v in value.items():
                new_key = f"{prefix}_{k}" if prefix else k
                flatten(new_key, v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                new_key = f"{prefix}_{i}" if prefix else f"{prefix}_{i}"
                flatten(new_key, v)
        else:
            key_clean = prefix.replace("_", " ")
            if key_clean == 'id':
                key_clean = 'objectId'
            lines.append(f"**{key_clean}:** {value}")

    flatten("", obj)
    return "\n".join(lines)


# ---------- Main Function ----------
def rag_from_json(json_path: str="", query: str="", top_k: int = 3):
    """
    Load JSON (list of objects), convert each record to Markdown,
    embed chunks in memory, and perform semantic RAG search.
    """
    import hashlib
    import time
    
    # Create in-memory Chroma collection with custom embedding function
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    
    # Create a unique collection name based on JSON path and timestamp
    json_hash = hashlib.md5(json_path.encode()).hexdigest()[:8]
    timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp
    collection_name = f"temp_json_rag_{json_hash}_{timestamp}"
    
    try:
        # Create a custom embedding function for queries
        class CustomEmbeddingFunction:
            def __call__(self, input):
                return embed_texts(input)
            
            def embed_query(self, input, **kwargs):
                embeddings = embed_texts([input])
                result = embeddings[0] if embeddings else []
                # ChromaDB expects a list of lists even for single query
                return [result]
        
        # Try to delete existing collection if it exists, then create new one
        try:
            client.delete_collection(name=collection_name)
        except:
            pass  # Collection doesn't exist, which is fine
        
        collection = client.create_collection(
            name=collection_name,
            embedding_function=CustomEmbeddingFunction()
        )

        # Load JSON data
        # with open(json_path, "r", encoding="utf-8") as f:
        #     data = json.load(f)
        data = get_board_items()

        # Normalize: list of dicts
        if isinstance(data, dict):
            data = [data]

        # Convert each object to Markdown string
        md_blocks = [json_to_markdown(obj) for obj in data]

        # Chunk each Markdown block
        # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # chunks = []
        # for block in md_blocks:
        #     chunks.extend(splitter.split_text(block))
        chunks = md_blocks
        # Embed and store in Chroma
        embeddings = embed_texts(chunks)
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Suppress any output from ChromaDB by redirecting stdout and stderr
        import sys
        import os
        from contextlib import redirect_stdout, redirect_stderr
        
        # Save original stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirect to devnull
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                collection.add(documents=chunks, embeddings=embeddings, ids=ids)
            finally:
                # Restore original stdout and stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        # Query
        results = collection.query(query_texts=[query], n_results=top_k)
        context = "\n".join(results["documents"][0])
        
        # TEMPORARY FIX: Disable EASL to prevent timeout errors
        # TODO: Re-enable EASL once connectivity issues are resolved
        # easl_question = f"Question: {query}\nContext: {context}"
        # easl_answer = get_easl_answer(easl_question)
        # rag_res = f"RAG Result: {context}\nEASL Answer: {easl_answer}"
        
        # Return RAG results only for now (more reliable)
        return context
        
    finally:
        # Clean up: delete the temporary collection
        try:
            client.delete_collection(name=collection_name)
        except:
            pass  # Collection might already be deleted, which is fine



## RUN THIS FOR FIRST TIME TO CREATE VECTOR STORE
# collection = build_chroma_from_texts("patient_data", "./chroma_store")
# print("✅ Collection built successfully!")
    
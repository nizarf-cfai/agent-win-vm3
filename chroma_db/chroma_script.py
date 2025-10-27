import os, json, requests
import chromadb
from chromadb.config import Settings
from typing import List
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import time
import numpy as np  # For OpenAI RAG cosine similarity
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

# OpenAI RAG Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # Cost-effective, fast
EMBEDDING_CACHE = {}  # Cache embeddings to avoid repeated API calls

# ============================================================================
# OPENAI-BASED RAG FUNCTIONS (NEW - PRIMARY SYSTEM)
# ============================================================================

def create_embedding_openai(text: str) -> List[float]:
    """Create embedding using OpenAI API"""
    # Check cache first
    if text in EMBEDDING_CACHE:
        return EMBEDDING_CACHE[text]
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": EMBEDDING_MODEL
        }
        
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            embedding = response.json()['data'][0]['embedding']
            EMBEDDING_CACHE[text] = embedding  # Cache it
            return embedding
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error creating embedding: {e}")
        return []


def cosine_similarity_openai(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def item_to_searchable_text_openai(item: dict) -> str:
    """
    Convert board item to searchable text with SMART PRIORITY TAGGING
    
    Priority Levels:
    🔥 SUMMARY ITEMS: Patient Context, Lab Findings, Adverse Events, Differential Diagnosis
    📊 TIMELINE ITEMS: Encounter Timeline (detailed chronological view)
    📝 INDIVIDUAL ENCOUNTERS: Single encounter cards (Encounter 1-6)
    🔬 RAW DATA: Nervecentre, ICE lab data (backend source data)
    """
    parts = []
    
    # Determine item priority and add strategic tags
    item_id = item.get('id', '').lower()
    component_type = item.get('componentType', '')
    title = item.get('content', {}).get('title', '') if isinstance(item.get('content'), dict) else ''
    
    # 🔥 PRIORITY 1: SUMMARY ITEMS (High-level overviews)
    is_summary = False
    if component_type == 'PatientContext' or 'patient-context' in item_id:
        parts.append("🔥 SUMMARY ITEM - HIGHEST PRIORITY")
        parts.append("KEYWORDS: patient overview, patient summary, patient info, demographics, patient context, sarah miller, about patient, patient profile, medical history summary, quick view, patient snapshot")
        parts.append("ITEM_TYPE: PRIMARY_PATIENT_SUMMARY")
        is_summary = True
    elif component_type == 'LabTable' or 'lab-table' in item_id or 'lab findings' in title.lower():
        parts.append("🔥 SUMMARY ITEM - HIGHEST PRIORITY")
        parts.append("KEYWORDS: lab results, lab findings, lab summary, laboratory, labs, lab data, test results, lab values, lab overview, lab report")
        parts.append("ITEM_TYPE: LAB_SUMMARY")
        is_summary = True
    elif component_type == 'LabChart' or 'lab-chart' in item_id or 'lab trends' in title.lower():
        parts.append("🔥 SUMMARY ITEM - HIGHEST PRIORITY")
        parts.append("KEYWORDS: lab trends, lab chart, lab graph, lab visualization, trending labs, lab timeline, lab changes over time")
        parts.append("ITEM_TYPE: LAB_TRENDS")
        is_summary = True
    elif component_type == 'AdverseEventAnalytics' or 'adverse' in item_id:
        parts.append("🔥 SUMMARY ITEM - HIGHEST PRIORITY")
        parts.append("KEYWORDS: adverse events, DILI, liver injury, side effects, adverse reactions, safety events, drug reactions, complications")
        parts.append("ITEM_TYPE: ADVERSE_EVENT_SUMMARY")
        is_summary = True
    elif component_type == 'DifferentialDiagnosis' or 'differential' in item_id:
        parts.append("🔥 SUMMARY ITEM - HIGHEST PRIORITY")
        parts.append("KEYWORDS: differential diagnosis, diagnosis, diagnostic, conditions, possible diagnoses, DDx, differential")
        parts.append("ITEM_TYPE: DIFFERENTIAL_DIAGNOSIS")
        is_summary = True
    
    # 📊 PRIORITY 2: TIMELINE ITEMS (Detailed chronological view)
    elif component_type == 'EncounterTimeline' or 'encounter-timeline' in item_id:
        parts.append("📊 TIMELINE ITEM - HIGH PRIORITY")
        parts.append("KEYWORDS: timeline, encounter timeline, chronological, visit history, full timeline, all encounters, complete history")
        parts.append("ITEM_TYPE: ENCOUNTER_TIMELINE")
    
    # 📝 PRIORITY 3: INDIVIDUAL ENCOUNTER CARDS
    elif 'single-encounter' in item_id or 'encounter #' in title.lower():
        # Extract encounter number
        enc_num = ""
        if 'encounter-6' in item_id or 'encounter #6' in title.lower():
            enc_num = "6 (LATEST, MOST RECENT, EMERGENCY VISIT)"
            parts.append("📝 INDIVIDUAL ENCOUNTER - LATEST/RECENT")
            parts.append("KEYWORDS: latest encounter, most recent, recent visit, last encounter, emergency, encounter 6, newest")
        elif 'encounter-5' in item_id or 'encounter #5' in title.lower():
            enc_num = "5 (SECOND MOST RECENT, SINUSITIS)"
            parts.append("📝 INDIVIDUAL ENCOUNTER - SECOND LATEST")
            parts.append("KEYWORDS: recent encounter, encounter 5, sinusitis visit")
        elif 'encounter-4' in item_id or 'encounter #4' in title.lower():
            enc_num = "4"
        elif 'encounter-3' in item_id or 'encounter #3' in title.lower():
            enc_num = "3"
        elif 'encounter-2' in item_id or 'encounter #2' in title.lower():
            enc_num = "2"
        elif 'encounter-1' in item_id or 'encounter #1' in title.lower():
            enc_num = "1 (FIRST, INITIAL CONSULT)"
            parts.append("📝 INDIVIDUAL ENCOUNTER - FIRST")
            parts.append("KEYWORDS: first encounter, initial, initial consult, first visit")
        
        parts.append(f"ITEM_TYPE: SINGLE_ENCOUNTER_{enc_num}")
        parts.append(f"KEYWORDS: encounter {enc_num}, visit {enc_num}, individual encounter")
    
    # 🔬 PRIORITY 4: RAW DATA SOURCES
    elif 'nervecentre' in item_id or 'raw-ice' in item_id:
        parts.append("🔬 RAW DATA ITEM - LOW PRIORITY")
        parts.append("ITEM_TYPE: RAW_BACKEND_DATA")
        parts.append("NOTE: This is backend source data, prefer dashboard summaries")
    
    # Add objectId
    if 'id' in item:
        parts.append(f"ObjectID: {item['id']}")
    
    # Add description
    if 'obj_description' in item and item['obj_description']:
        parts.append(f"Description: {item['obj_description']}")
    
    # Add title
    if title:
        parts.append(f"Title: {title}")
    
    # Add component type
    if component_type:
        parts.append(f"Component: {component_type}")
    
    # Add content-specific keywords
    if 'content' in item and isinstance(item['content'], dict):
        content = item['content']
        
        # Add props data (simplified)
        if 'props' in content:
            props = content['props']
            
            # Extract key information from props
            if isinstance(props, dict):
                # For patient data
                if 'patientData' in props:
                    parts.append("Contains: Patient information, demographics, medication timeline, problem list")
                
                # For encounters
                if 'encounters' in props:
                    parts.append("Contains: Multiple patient encounters, visit history, clinical progression")
                
                # For lab data
                if 'labs' in props or 'labData' in props:
                    parts.append("Contains: Laboratory test results, values, reference ranges")
                
                # For encounter data
                if 'encounter' in props:
                    enc = props['encounter']
                    if isinstance(enc, dict):
                        if 'meta' in enc:
                            meta = enc['meta']
                            if 'date_time' in meta:
                                parts.append(f"Date: {meta['date_time']}")
                        if 'reason_for_visit' in enc:
                            parts.append(f"Reason: {enc['reason_for_visit']}")
    
    return "\n".join(parts)


def rag_from_json_openai(query: str, top_k: int = 3) -> str:
    """
    Perform RAG search using OpenAI embeddings
    
    Args:
        query: User's search query
        top_k: Number of top results to return
        
    Returns:
        JSON string with matching board items and their objectIds
    """
    print(f"🔍 OpenAI RAG: Searching for '{query}'")
    
    # Detect "latest/recent" keywords
    query_lower = query.lower()
    wants_latest = any(keyword in query_lower for keyword in ['latest', 'recent', 'most recent', 'last'])
    
    # Get board items
    board_items = get_board_items()
    if not board_items:
        print("❌ No board items available")
        return json.dumps([])
    
    # Create query embedding
    print(f"📊 Creating embedding for query...")
    query_embedding = create_embedding_openai(query)
    if not query_embedding:
        print("❌ Failed to create query embedding")
        return json.dumps([])
    
    # Calculate similarities for each item
    print(f"🔢 Calculating similarities for {len(board_items)} items...")
    similarities = []
    
    for item in board_items:
        # Convert item to searchable text
        item_text = item_to_searchable_text_openai(item)
        
        # Create embedding for item
        item_embedding = create_embedding_openai(item_text)
        
        if item_embedding:
            # Calculate similarity
            similarity = cosine_similarity_openai(query_embedding, item_embedding)
            
            # 🔥 BOOST SCORE for latest/recent items
            boost = 0.0
            if wants_latest:
                # Check if this is a recent encounter (encounter 5 or 6)
                item_id = item.get('id', '')
                if 'encounter-6' in item_id or 'encounter-5' in item_id:
                    boost = 0.3  # Significant boost for latest encounters
                    print(f"   🚀 BOOSTING '{item_id}' for latest query (+{boost})")
                elif 'encounter' in item_id and any(num in item_id for num in ['1', '2', '3', '4']):
                    boost = -0.1  # Slight penalty for older encounters
            
            final_score = similarity + boost
            
            similarities.append({
                'item': item,
                'similarity': final_score,
                'original_similarity': similarity,
                'boost': boost,
                'text': item_text
            })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Get top K results
    top_results = similarities[:top_k]
    
    print(f"✅ Found {len(top_results)} matches")
    for i, result in enumerate(top_results, 1):
        print(f"   {i}. {result['item'].get('id', 'NO_ID')} (similarity: {result['similarity']:.3f})")
    
    # Format results for return
    formatted_results = []
    for result in top_results:
        item = result['item']
        formatted_results.append({
            'objectId': item.get('id', ''),
            'description': item.get('obj_description', ''),
            'title': item.get('content', {}).get('title', '') if isinstance(item.get('content'), dict) else '',
            'component': item.get('content', {}).get('component', '') if isinstance(item.get('content'), dict) else '',
            'similarity_score': round(result['similarity'], 3),
            'matched_text': result['text'][:200]  # First 200 chars of matched text
        })
    
    return json.dumps(formatted_results, indent=2)

# ============================================================================
# END OPENAI RAG FUNCTIONS
# ============================================================================

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
    
    NOW WITH TRIPLE FALLBACK:
    1. OpenAI RAG (Primary - fast, reliable)
    2. ChromaDB RAG (Fallback - if OpenAI fails)
    3. Direct mapping (Last resort - query_to_objectid_mapper)
    """
    import hashlib
    import time
    
    # 🔥 PRIMARY: Try OpenAI RAG first (faster, more reliable)
    if OPENAI_API_KEY:
        try:
            print(f"🚀 Attempting OpenAI RAG (primary)...")
            result = rag_from_json_openai(query, top_k)
            if result and result != "[]":
                print(f"✅ OpenAI RAG succeeded!")
                return result
            else:
                print(f"⚠️ OpenAI RAG returned empty results, trying ChromaDB fallback...")
        except Exception as e:
            print(f"⚠️ OpenAI RAG failed: {e}, trying ChromaDB fallback...")
    else:
        print(f"⚠️ No OpenAI API key, using ChromaDB...")
    
    # 🔥 FALLBACK: Use ChromaDB RAG (original system)
    
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

import requests
import json
import time
import aiohttp
import helper_model
import os
import asyncio
from typing import Optional, Dict, Any

BASE_URL = os.getenv("CANVAS_URL", "https://board-v25.vercel.app")

print(f"🌐 Canvas Operations configured with BASE_URL: {BASE_URL}")

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 2.0


async def retry_async_operation(operation, max_retries=MAX_RETRIES, operation_name="operation"):
    """
    Generic retry wrapper for async operations
    Implements exponential backoff with jitter
    """
    retry_delay = INITIAL_RETRY_DELAY
    last_error = None
    
    for attempt in range(max_retries):
        try:
            result = await operation()
            if attempt > 0:
                print(f"  ✅ {operation_name} succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Add jitter to prevent thundering herd
                jitter = retry_delay * 0.1 * (hash(str(e)) % 10) / 10
                wait_time = min(retry_delay + jitter, MAX_RETRY_DELAY)
                
                print(f"  ⚠️ {operation_name} attempt {attempt + 1} failed: {str(e)[:50]}")
                print(f"     Retrying in {wait_time:.2f}s...")
                
                await asyncio.sleep(wait_time)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"  ❌ {operation_name} failed after {max_retries} attempts")
    
    raise last_error


async def get_agent_answer(todo):
    """Get agent answer with retry logic"""
    async def _get_answer():
        data = await helper_model.generate_response(todo)
        result = {
            'content': data.get('answer', ''),
        }
        if todo.get('title'):
            result['title'] = todo.get('title', '').lower().replace("to do", "Result").capitalize()
        return result
    
    return await retry_async_operation(_get_answer, operation_name="Agent Answer")


def get_canvas_item_id():
    """Sync version - fetches canvas items description"""
    url = BASE_URL + "/api/board-items"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        item_desc = []
        for item in data:
            rec = {
                'objectId': item['id'],
                'description': item.get('obj_description', ''),
                'content_type': item.get('content', '')
            }

            if item.get('agentData'):
                rec['content'] = item.get('agentData')
            elif item.get('todoItems'): 
                rec['content'] = item.get('todoItems')
            else:
                rec['content'] = item.get('ehrData', {}).get('subjective')
            
            item_desc.append(rec)

        # Save for debugging
        with open("item_desc.json", "w", encoding="utf-8") as f:
            json.dump(item_desc, f, ensure_ascii=False, indent=2)
            
        return json.dumps(item_desc, indent=4)
    
    except Exception as e:
        print(f"❌ Error fetching canvas items: {e}")
        return json.dumps([])


async def focus_item(item_id: str, sub_element: str = "", max_retries: int = MAX_RETRIES) -> Dict[Any, Any]:
    """
    OPTIMIZED: Focus on canvas item with retry logic and validation
    
    Args:
        item_id: Object ID to focus on
        sub_element: Optional sub-element to focus on (e.g., "medications.methotrexate")
        max_retries: Number of retry attempts
    
    Returns:
        Response data from the API
    """
    
    async def _focus():
        url = BASE_URL + "/api/focus"
        payload = {
            "objectId": item_id,
            "subElement": sub_element,
            # "focusOptions": {
            #     "zoom": 1.8,
            #     "highlight": True,
            #     "duration": 500   # Animation duration in ms
            # }
        }

        
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                # Check if request was successful
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Focus API returned {response.status}: {error_text}")
                
                data = await response.json()
                
                # Validate response
                if not data or not isinstance(data, dict):
                    raise Exception(f"Invalid response format: {data}")
                
                # Save for debugging (only on success)
                try:
                    with open("focus_payload.json", "w", encoding="utf-8") as f:
                        json.dump(payload, f, ensure_ascii=False, indent=4)
                    with open("focus_response.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                except:
                    pass  # Don't fail on debug file write
                
                return data
    
    return await retry_async_operation(
        _focus, 
        max_retries=max_retries, 
        operation_name=f"Focus Item ({item_id[:20]}...)"
    )


async def create_todo(payload_body: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    OPTIMIZED: Create enhanced todo with retry logic
    
    Args:
        payload_body: Todo data structure
    
    Returns:
        Created todo response
    """
    
    async def _create():
        url = BASE_URL + "/api/enhanced-todo"
        timeout = aiohttp.ClientTimeout(total=30)  # Longer timeout for todo creation
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload_body) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise Exception(f"Todo API returned {response.status}: {error_text}")
                
                data = await response.json()
                
                # Validate response has ID
                if not data.get('id'):
                    raise Exception(f"Todo creation returned no ID: {data}")
                
                # Save for debugging
                try:
                    with open("todo_payload.json", "w", encoding="utf-8") as f:
                        json.dump(payload_body, f, ensure_ascii=False, indent=4)
                    with open("todo_response.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                except:
                    pass
                
                return data
    
    return await retry_async_operation(
        _create, 
        max_retries=MAX_RETRIES, 
        operation_name="Create Todo"
    )


async def create_lab(payload_body: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    OPTIMIZED: Create lab result with retry logic
    
    Args:
        payload_body: Lab result data
    
    Returns:
        Created lab result response
    """
    
    async def _create():
        url = BASE_URL + "/api/lab-results"
        timeout = aiohttp.ClientTimeout(total=15)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload_body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Lab API returned {response.status}: {error_text}")
                
                data = await response.json()
                
                # Validate response
                if not data.get('id'):
                    raise Exception(f"Lab creation returned no ID: {data}")
                
                return data
    
    return await retry_async_operation(
        _create, 
        max_retries=MAX_RETRIES, 
        operation_name="Create Lab Result"
    )


async def create_result(agent_result: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    OPTIMIZED: Create agent result with retry logic
    
    Args:
        agent_result: Agent analysis result
    
    Returns:
        Created result response
    """
    
    async def _create():
        url = BASE_URL + "/api/agents"
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=agent_result) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise Exception(f"Agent API returned {response.status}: {error_text}")
                
                data = await response.json()
                return data
    
    return await retry_async_operation(
        _create, 
        max_retries=MAX_RETRIES, 
        operation_name="Create Agent Result"
    )


# ============================================================================
# BATCH OPERATIONS FOR PERFORMANCE
# ============================================================================

async def batch_focus_items(item_ids: list[str], delay: float = 0.3) -> list[Dict[Any, Any]]:
    """
    Focus multiple items in sequence with controlled delays
    Useful for showing multiple related items
    
    Args:
        item_ids: List of object IDs to focus on
        delay: Delay between focus operations (seconds)
    
    Returns:
        List of focus responses
    """
    results = []
    for i, item_id in enumerate(item_ids):
        try:
            print(f"  📍 Focusing item {i+1}/{len(item_ids)}: {item_id[:30]}...")
            result = await focus_item(item_id)
            results.append(result)
            
            # Add delay between focuses (except after last item)
            if i < len(item_ids) - 1:
                await asyncio.sleep(delay)
        except Exception as e:
            print(f"  ⚠️ Failed to focus item {i+1}: {e}")
            results.append(None)
    
    return results


async def create_multiple_labs(lab_data_list: list[Dict[Any, Any]]) -> list[Dict[Any, Any]]:
    """
    Create multiple lab results in parallel for faster processing
    
    Args:
        lab_data_list: List of lab result data dictionaries
    
    Returns:
        List of created lab results
    """
    tasks = [create_lab(lab_data) for lab_data in lab_data_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and log them
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  ⚠️ Lab creation {i+1} failed: {result}")
        else:
            valid_results.append(result)
    
    return valid_results


# ============================================================================
# HEALTH CHECK AND DIAGNOSTICS
# ============================================================================

async def check_canvas_health() -> bool:
    """
    Check if canvas API is responsive
    
    Returns:
        True if healthy, False otherwise
    """
    try:
        url = BASE_URL + "/api/board-items"
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Canvas API healthy ({len(data)} items)")
                    return True
                else:
                    print(f"⚠️ Canvas API returned {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Canvas API unhealthy: {e}")
        return False


async def get_canvas_item_async(item_id: str) -> Optional[Dict[Any, Any]]:
    """
    Get a specific canvas item by ID
    
    Args:
        item_id: Object ID to retrieve
    
    Returns:
        Item data or None if not found
    """
    try:
        url = BASE_URL + "/api/board-items"
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    items = await response.json()
                    for item in items:
                        if item.get('id') == item_id:
                            return item
                    return None
                else:
                    return None
    except Exception as e:
        print(f"❌ Error getting canvas item: {e}")
        return None


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def focus_and_wait(item_id: str, sub_element: str = "", wait_time: float = 1.0):
    """
    Focus on item and wait for animation to complete
    Useful for ensuring smooth transitions
    """
    result = await focus_item(item_id, sub_element)
    await asyncio.sleep(wait_time)
    return result


async def create_todo_and_focus(payload_body: Dict[Any, Any], focus_delay: float = 2.0):
    """
    Create todo and automatically focus on it
    One-step operation for convenience
    """
    todo_result = await create_todo(payload_body)
    
    if todo_result and todo_result.get('id'):
        await asyncio.sleep(focus_delay)
        focus_result = await focus_item(todo_result['id'])
        return todo_result, focus_result
    
    return todo_result, None


async def create_lab_and_focus(payload_body: Dict[Any, Any], focus_delay: float = 1.0):
    """
    Create lab result and automatically focus on it
    One-step operation for convenience
    """
    lab_result = await create_lab(payload_body)
    
    if lab_result and lab_result.get('id'):
        await asyncio.sleep(focus_delay)
        focus_result = await focus_item(lab_result['id'])
        return lab_result, focus_result
    
    return lab_result, None
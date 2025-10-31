import requests
import json
import time
import aiohttp
import helper_model
import os



BASE_URL = os.getenv("CANVAS_URL", "https://board-v25.vercel.app")


async def get_agent_answer(todo,session_id=''):
    data = await helper_model.generate_response(todo,session_id=session_id)

    result = {}
    result['content'] = data.get('answer', '')
    if todo.get('title'):
        result['title'] = todo.get('title', '').lower().replace("to do", "Result").capitalize()

    return result



async def focus_item(item_id, sub_element="",session_id=""):

    url = BASE_URL + "/api/focus"
    payload = {
        "objectId": item_id,
        "subElement" : sub_element,
        "focusOptions": {
            "zoom": 0.8,
            "highlight": True
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            with open("focus_payload.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            data = await response.json()
            with open("focus_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data

async def create_todo(payload_body,session_id):

    url = BASE_URL + "/api/enhanced-todo"

    payload = payload_body
    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            with open("todo_payload.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            data = await response.json()
            with open("todo_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data
    
async def create_lab(payload_body,session_id):
   
    url = BASE_URL + "/api/lab-results"
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload_body, headers=headers) as response:
            data = await response.json()
            return data

async def create_result(agent_result,session_id):
    url = BASE_URL + "/api/agents"
    
    # agent_result['zone'] = "raw-ehr-data-zone"
    payload = agent_result
    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            return data
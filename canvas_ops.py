import requests
import json
import time
import aiohttp
import helper_model
import os
import httpx
import asyncio



os.environ["NO_PROXY"] = "*"


BASE_URL = os.getenv("CANVAS_URL", "https://board-v25.vercel.app")

HELPER_SERVER_URL = "http://localhost:3000"

async def get_agent_answer(todo,session_id=''):
    data = await helper_model.generate_response(todo,session_id=session_id)

    result = {}
    result['content'] = data.get('answer', '')
    if todo.get('title'):
        result['title'] = todo.get('title', '').lower().replace("to do", "Result").capitalize()

    return result



async def focus_item(session,item_id, sub_element="",session_id=""):

    url = BASE_URL + "/api/focus"
    payload = {
        "objectId": item_id,
        "subElement" : sub_element,
        "focusOptions": {
            "zoom": 0.8,
            "highlight": True,
            "duration": 1200,
            "scrollIntoView": True
        }
    }


    response = session.post(url, json=payload)
    print("Focus URL:",url)
    print("Focus Session Headers:",session.headers)
    print("Focus Status Code:", response.status_code)
    print("Focus Headers:", response.headers)
    with open("focus_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("focus_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url, json=payload, headers=headers) as response:
    #         with open("focus_payload.json", "w", encoding="utf-8") as f:
    #             json.dump(payload, f, ensure_ascii=False, indent=4)
    #         data = await response.json()
    #         with open("focus_response.json", "w", encoding="utf-8") as f:
    #             json.dump(data, f, ensure_ascii=False, indent=4)
    #         return data

async def focus_item2(item_id, sub_element="",session_id=""):
    url = "http://localhost:3000/send-post-request"

    payload = {
        "url" : 'https://board-v2-test-self.vercel.app/api/focus',
        "payload":{
            "sessionId": session_id, 
            "objectId": item_id,
            }
        
    }
    response = requests.post(url,json=payload)
    # print(response.json())
    with open("focus_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("focus_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

async def create_todo(payload_body,session_id):

    url = BASE_URL + f"/api/enhanced-todo?sessionId={session_id}"

    payload = payload_body

    response = requests.post(url, json=payload)
    print("CREATE TODO RESPONSE:", response.status_code)
    print("CREATE TODO HEADERS:", response.headers)
    with open("todo_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("todo_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url, json=payload, headers=headers) as response:
    #         print("CREATE TODO RESPONSE:", response.status)
    #         with open("todo_payload.json", "w", encoding="utf-8") as f:
    #             json.dump(payload, f, ensure_ascii=False, indent=4)
    #         data = await response.json()
    #         with open("todo_response.json", "w", encoding="utf-8") as f:
    #             json.dump(data, f, ensure_ascii=False, indent=4)
    #         return data

    # async with httpx.AsyncClient(http2=False, timeout=30.0) as client:
    #     response = await client.post(url, json=payload_body, headers=headers)
    # print("CREATE TODO RESPONSE:", response.status_code)
    # print("CREATE TODO HEADERS:", response.headers)

    # # Save payload and response to JSON files (for debugging)
    # with open("todo_payload.json", "w", encoding="utf-8") as f:
    #     json.dump(payload_body, f, ensure_ascii=False, indent=4)
    # data = response.json()
    # with open("todo_response.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # return data

def create_todo2(payload_body,session_id):
    url = "http://localhost:3000/send-post-request"

    payload_body['sessionId'] = session_id

    payload = {
        "url" : 'https://board-v2-test-self.vercel.app/api/enhanced-todo',
        "payload":payload_body
        
    }
    response = requests.post(url,json=payload)
    # print(response.json())
    with open("todo_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("todo_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data.get('item',{})

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
            return data.get('item',{})

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
            return data.get('item',{})
        
async def create_result(agent_result,session_id):
    url = "http://localhost:3000/send-post-request"

    agent_result['sessionId'] = session_id

    payload = {
        "url" : 'https://board-v2-test-self.vercel.app/api/agents',
        "payload":agent_result
        
    }
    response = requests.post(url,json=payload)
    # print(response.json())
    with open("agentres_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("agentres_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data.get('item',{})
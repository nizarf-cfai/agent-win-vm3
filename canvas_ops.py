import requests
import json
import time
import aiohttp
import helper_model

# BASE_URL = "http://localhost:3001"
BASE_URL = "https://patientcanvas-ai.vercel.app"
AGENT_URL = "http://localhost:8000"

async def get_agent_answer(todo):
    data = await helper_model.generate_response(todo)
    # data = await response.json()
    result = {}
    result['content'] = data.get('answer', '')
    if todo.get('title'):
        result['title'] = todo.get('title', '').lower().replace("to do", "Result").capitalize()

    return result

def get_canvas_item_id():
    # with open("canvas-data.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # items_data = []
    # for d in data['boxes']:
    #     items_data.append(
    #         {
    #             'id': d['id'],
    #             'name': d['title'],
    #             "content": d['content'],
    #             "items": d.get('items', [])
    #         }
    #     )
    
    # return json.dumps(items_data, indent=4)
    url = BASE_URL + "/api/board-items"
    
    response = requests.get(url)
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
            rec['content'] = item.get('ehrData',{}).get('subjective')
        item_desc.append(rec)


    with open("item_desc.json", "w", encoding="utf-8") as f:
        json.dump(item_desc, f, ensure_ascii=False, indent=2)
        
    return json.dumps(item_desc, indent=4)


async def focus_item(item_id):
    # url = BASE_URL + "/api/focus-item"
    # payload = {
    # "itemId": item_id  # change to the ID of an existing box
    # }
    url = BASE_URL + "/api/focus"
    payload = {
        "objectId": item_id 
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return data

async def create_todo(payload_body):
    # url = BASE_URL + "/api/add-box"
    # real_payload = {}
    # real_payload['title'] = payload_body['title']
    # real_payload['content'] = payload_body['content']
    # real_payload['area'] = payload_body['area']
    # real_payload['items'] = []
    # for i in payload_body['items']:
    #     real_payload['items'].append({
    #         "id": "",
    #         "text": i,
    #         "status": "active",
    #         "priority":"high"
    #     })

    url = BASE_URL + "/api/todos"
    real_payload = {}
    real_payload['title'] = payload_body['title']
    real_payload['description'] = payload_body['content']
    real_payload['todo_items'] = []

    for i in payload_body['items']:
        real_payload['todo_items'].append(i)

    payload = real_payload

    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return data
    
async def create_lab(payload_body):
   
    url = BASE_URL + "/api/lab-results"
    

    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload_body) as response:
            data = await response.json()
            return data

async def create_result(agent_result):
    url = BASE_URL + "/api/agents"
    

    payload = agent_result

    # response = requests.post(url, json=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return data
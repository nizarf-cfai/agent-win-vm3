import asyncio
import requests
import json

BASE_URL = "https://board-v2-test-self.vercel.app"

async def create_todo(payload_body,session_id):

    url = BASE_URL + "/api/enhanced-todo"

    payload = payload_body
    headers = {
        "Content-Type": "application/json",
        "Session-Id": session_id
    }
    
    response = requests.post(url, json=payload,headers=headers)
    print("CREATE TODO RESPONSE:", response.status_code)
    print("CREATE TODO HEADERS:", response.headers)
    with open("todo_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    data = response.json()
    with open("todo_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


session_id = "b83f7348-d31f-4664-af32-6efcd9205dc4"
data = {
      "title": "Patient Admission Workflow",
      "description": "Comprehensive patient admission process with detailed sub-tasks",
      "todos": [
        {
          "id": "task-101",
          "text": "Initial Patient Assessment",
          "status": "executing",
          "agent": "Assessment Agent",
          "subTodos": [
            {
              "text": "Check vital signs",
              "status": "finished"
            },
            {
              "text": "Review medical history",
              "status": "executing"
            },
            {
              "text": "Document chief complaint",
              "status": "pending"
            }
          ]
        },
        {
          "id": "task-102",
          "text": "Laboratory Testing",
          "status": "pending",
          "agent": "Lab Coordination Agent",
          "subTodos": [
            {
              "text": "Order blood work",
              "status": "pending"
            },
            {
              "text": "Schedule imaging studies",
              "status": "pending"
            },
            {
              "text": "Collect urine sample",
              "status": "pending"
            }
          ]
        },
        {
          "id": "task-103",
          "text": "Treatment Planning",
          "status": "finished",
          "agent": "Treatment Planning Agent",
          "subTodos": [
            {
              "text": "Consult with specialists",
              "status": "finished"
            },
            {
              "text": "Develop care plan",
              "status": "finished"
            },
            {
              "text": "Set treatment goals",
              "status": "finished"
            }
          ]
        }
      ]
    }



asyncio.run(create_todo(data,session_id))


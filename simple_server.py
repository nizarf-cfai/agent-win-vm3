from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import httpx  # async alternative to requests

app = FastAPI()

# Define the expected structure of the incoming JSON payload
class RequestData(BaseModel):
    url: str
    payload: Dict[str, Any]  # nested JSON object


# ✅ Async health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}


# ✅ Async POST endpoint
@app.post("/send-post-request")
async def send_request(data: RequestData):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(data.url, json=data.payload)
            print("➡️ Payload:", data.payload)

            # Try to parse JSON response
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}
        except ValueError:
            # In case response is not JSON
            return {"status": response.status_code, "text": response.text}

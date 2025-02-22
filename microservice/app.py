import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn
import random
import json
from nats.aio.client import Client as NATS

app = FastAPI()
nats_client = NATS()

@app.on_event("startup")
async def startup_event():
    await nats_client.connect(servers=["nats://nats:4222"])
    
    async def request_handler(msg):
        # Process the incoming request message and reply.
        try:
            payload = json.loads(msg.data.decode())
            # Simulate processing or random failure (1 in 10 chance)
            if random.randint(1, 10) == 1:
                response = {"error": "Random Failure Occurred"}
            else:
                response = {"message": "Hello from the FastAPI mock microservice", "input": payload}
            await nats_client.publish(msg.reply, json.dumps(response).encode())
        except Exception as e:
            await nats_client.publish(msg.reply, json.dumps({"error": str(e)}).encode())
    
    # Subscribe to a subject that the API gateway will use (e.g., "mock.request")
    await nats_client.subscribe("mock.request", cb=request_handler)

@app.get("/health")
async def health_check():
    # Optional HTTP health endpoint (useful for container-level health checks)
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import json
from nats.aio.client import Client as NATS

app = FastAPI()
nats_client = NATS()

# On startup, connect to the NATS broker (using the Docker service name "nats")
@app.on_event("startup")
async def startup_event():
    try:
        await nats_client.connect(servers=["nats://nats:4222"])
    except Exception as e:
        raise RuntimeError(f"Error connecting to NATS broker: {e}")

# Clean up on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    if nats_client.is_connected:
        await nats_client.close()

# An endpoint that uses NATS request/reply messaging to communicate with a downstream service.
# The gateway publishes a JSON payload to the provided subject and waits for a response.
@app.post("/request/{subject}")
async def request_subject(subject: str, request: Request):
    payload = await request.json()
    try:
        msg = await nats_client.request(subject, json.dumps(payload).encode(), timeout=2)
        data = json.loads(msg.data.decode())
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable: " + str(e))

# A simple publish endpoint if you need fire-and-forget messaging
@app.post("/publish/{subject}")
async def publish(subject: str, request: Request):
    payload = await request.json()
    await nats_client.publish(subject, json.dumps(payload).encode())
    return {"status": "published"}
    
# Basic self-health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}
# Health-check endpoint for verifying connectivity to the NATS broker.
@app.get("/health/nats")
async def health_nats():
    if nats_client.is_connected:
        return {"nats": "healthy"}
    else:
        raise HTTPException(status_code=503, detail="NATS broker is unreachable")

from fastapi import FastAPI
from server.environment import EmailEnvironment
from models import EmailAction
app = FastAPI()

env = EmailEnvironment()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/reset")
async def reset():
    result = await env.reset()
    return result


@app.post("/step")
async def step(action: EmailAction):
    result = await env.step(action)
    return result


@app.get("/state")
async def state():
    return await env.state()
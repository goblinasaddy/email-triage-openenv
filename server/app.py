from fastapi import FastAPI
from openenv_core.server import create_fastapi_app
from server.environment import EmailEnvironment

app = create_fastapi_app(EmailEnvironment)

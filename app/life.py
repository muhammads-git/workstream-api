from contextlib import asynccontextmanager


from fastapi import FastAPI
from app.services.connection_manager import ConnectionManager

@asynccontextmanager
async def lifespan(app: FastAPI):
   # startup
   app.state.manager = ConnectionManager()

   yield

   # shuttdown 


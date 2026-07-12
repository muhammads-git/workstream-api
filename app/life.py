from contextlib import asynccontextmanager


from fastapi import FastAPI
from app.services.connection_manager import ConnectionManager
from app.schedular.background_schedular import start_schedular,shuttdown_schedular

@asynccontextmanager
async def lifespan(app: FastAPI):
   # startup
   app.state.manager = ConnectionManager()
   start_schedular()

   yield

   # shuttdown
   shuttdown_schedular()
   


from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.connection_manager import ConnectionManager
from app.schedular.background_schedular import start_schedular,shutdown_schedular
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
   # startup
   app.state.manager = ConnectionManager()
   # redis startup
   app.state.redis = Redis(host='localhost', port=6379,decode_responses=True)
   start_schedular()

   yield

   # shuttdown
   shutdown_schedular()
   await app.state.redis.close()
   


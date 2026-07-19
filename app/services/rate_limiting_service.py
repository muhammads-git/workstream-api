from fastapi import HTTPException,status
from datetime import datetime,timedelta,timezone

async def checkRateLimit(redis, user_id : int, max_req : int = 5, time_window : int = 60):

   key = f'rate_limit:{user_id}'

   count = await redis.incr(key)

   if count == 1:
      # set expiry if this is first request
      await redis.expire(key,time_window)
   elif count > max_req:
      raise HTTPException(status_code=429, detail='Too many requests, slow down.')
   
from passlib.context import CryptContext
from jose import jwt
import os 
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends


# set up the CryptContext with basics scheme bcrypt
pwd_context = CryptContext(schemes=['argon2'],deprecated='auto')


def hashPassword(plain_password:str) -> str:
      return pwd_context.hash(plain_password)
   
def checkPassword(plain_password:str,hashed_password:str) -> bool:
      return pwd_context.verify(plain_password,hashed_password)
   
# SETUP JWT
# attributes.. for Creating Access Token....
ALGORITHM = os.getenv('JWT_ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')


def createAccessToken(data:dict):
      """ Here, encode those headers + payload + signature """
      payload = data.copy()
      expire = datetime.now(timezone.utc) + timedelta(minutes=30)
      payload.update({"exp": expire})
      token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
      return token
   
def decodeToken(token):
      """ Here, decode the token,, using jwt.decode and then return ... """
      try:
         payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
         username = payload.get('sub')
         user_id = payload.get('id')
         return {'username':username,'user_id':user_id}
      except Exception as e:
         print(f'Invalid Token..: {e}')
         return None

### get current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
def get_current_user(token:str = Depends(oauth2_scheme))-> str:
      payload = decodeToken(token=token)
      if not payload:
          raise HTTPException(status_code=401,detail='Invalid token')
      return payload
   
        
    
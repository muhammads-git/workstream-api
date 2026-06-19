from passlib.context import CryptContext
from jose import jwt
import os 
from datetime import datetime,timedelta,timezone

# attributes.. for Creating Access Token....
ALGORITHM = os.getenv('JWT_ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')

# set up the CryptContext with basics scheme bcrypt
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class Passwords:

   def hashPassword(plain_password:str) -> str:
      return pwd_context.hash(plain_password)
   
   def checkPassword(plain_password:str,hashed_password:str) -> bool:
      return pwd_context.verify(plain_password,hashed_password)
   
# SETUP JWT

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
         username = jwt.decode(token=token)
         return username
      except Exception as e:
         print(f'Invalid Token..: {e}')
         return None


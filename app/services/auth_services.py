from passlib.context import CryptContext
from jose import jwt


# set up the CryptContext with basics scheme bcrypt
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class Passwords:

   def hashPassword(plain_password:str) -> str:
      return pwd_context.hash(plain_password)
   
   def checkPassword(plain_password:str,hashed_password:str) -> bool:
      return pwd_context.verify(plain_password,hashed_password)
   


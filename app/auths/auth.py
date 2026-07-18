from fastapi import APIRouter, Request, HTTPException,Depends
from app.database import get_db,SessionLocal
from app.schema import UserCreate,UserLogin,UserResponse
from sqlalchemy.orm import Session
from app.services.auth_services import checkPassword,hashPassword
from app.models import User
from app.services.auth_services import createAccessToken
from fastapi.security import OAuth2PasswordRequestForm
# router..
auths_router = APIRouter()


@auths_router.post('/register',response_model=UserResponse)
def register(request:Request,user:UserCreate, db:Session= Depends(get_db)):
   # chech for existing user
   existing = db.query(User).filter(User.email == user.email).first()
   if existing:
      raise HTTPException(status_code=400,detail="Email already exits!")
   # hash password 
   hashed_password = hashPassword(user.password)
   # insert
   new_user =  User(
      name = user.name,
      email = user.email,
      password = hashed_password
   )
   # commit
   db.add(new_user)
   db.commit()
   db.refresh(new_user)

   return new_user

@auths_router.post('/login')
def login(user:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
   user_data = db.query(User).filter(User.email == user.username).first()
   if user_data and checkPassword(user.password,user_data.password):
      # check password
      # username = user_data.name
      # create token
      token = createAccessToken(data={'sub':user_data.name,'id':user_data.id})
      return {'access_token': token, 'token_type': 'bearer'}
   raise HTTPException(status_code=401, detail="Invalid credentials")


## get current User

@auths_router.post('/logout')
def logout():
   pass
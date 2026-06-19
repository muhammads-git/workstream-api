from fastapi import APIRouter, Request, HTTPException,Depends
from app.database import get_db,SessionLocal
from app.schema import UserCreate,UserLogin,UserResponse
from sqlalchemy.orm import Session
from app.services.auth_services import Passwords
from app.models import User
from app.services.auth_services import Tokens
# router..
auths_router = APIRouter()


@auths_router.post('/register',response_model=UserResponse)
def register(request:Request,user:UserCreate, db:Session= Depends(get_db)):
   # chech for existing user
   existing = db.query(User).filter(user.email == User.email).all()
   if existing:
      raise HTTPException(status_code=400,detail="Email already exits!")
   # hash password 
   hashed_password = Passwords.hashPassword(user.password)
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
def login(user:UserLogin,db:Session = Depends(get_db)):
   # verify 
   # create access token
   # success
   user_data = db.query(User).filter(user.email == User.email).all()
   if user_data :
      username = user_data.name
      # create token
      token = Tokens.createAccessToken(data=[username])
      return {'token':token,'message':'User log-In Success'}
   return {'message':'User not found'}



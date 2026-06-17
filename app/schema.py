from pydantic import BaseModel, EmailStr

# register
class UserCreate(BaseModel):
   name : str
   email : EmailStr
   password : str

# login
class UserLogin(BaseModel):
   email : EmailStr
   password : str

# response
class UserResponse(BaseModel):
   id : int
   name : str
   email : EmailStr

   class Config:
        from_attributes = True
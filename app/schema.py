from pydantic import BaseModel, EmailStr
from app.models import MemberRole
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

# organization
class OrganizationForm(BaseModel):
   name : str

   class Config:
        from_attributes = True

class AddMemberSchema(BaseModel):
   email : EmailStr
   # role : MemberRole = MemberRole.member


class ProjectCreate(BaseModel):
   title : str
   org_id : int
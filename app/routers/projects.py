from fastapi import APIRouter,HTTPException,Depends
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole

pro_router = APIRouter()



@pro_router.post('/project')
def create_project(db : Session = Depends(get_db), cur_user = Depends(get_current_user)):
   pass
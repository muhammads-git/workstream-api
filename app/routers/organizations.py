"""
   Create Organizations:
   Invite Members:


"""

from fastapi import APIRouter,HTTPException,Depends
from app.schema import OrganizationForm
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization



org_router = APIRouter()


@org_router.post('/organization')
def create_organization(org_name : OrganizationForm, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):
   # authentications layer
   print(cur_user)
   if not cur_user:
      raise HTTPException(status_code=401, detail='No user found, login again!')
   
   # db
   user_id = cur_user.get('user_id')
   user_name  = cur_user.get('username')

   new_org = Organization(name=org_name.name,created_by=user_id)
   db.add(new_org)
   db.commit()

   return {
    'message': 'Organization created successfully',
    'organization': {
        'name': org_name.name,
        'created_by': user_name
    }
}

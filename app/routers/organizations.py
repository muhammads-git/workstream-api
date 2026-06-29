"""
   Create Organizations:
   Invite Members:


"""

from fastapi import APIRouter,HTTPException,Depends
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole

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
   db.flush() # gets the new_org id without full commit

   # automatically add creator ad admin.
   membership = Membership(
      user_id=user_id,
      org_id=new_org.id,
      role=MemberRole.admin
      )

   db.add(membership)
   db.commit()
   db.refresh(new_org)

   ### membership table main.. ye user id ... usko as admin role dena..
   return {
    'message': 'Organization created successfully',
    'organization': {
         'ID' : new_org.id,
        'name': org_name.name,
        'created_by': user_name
    }
}



@org_router.post('/organizations/{org_id}/invite')
def invite_members(org_id : int,member : AddMemberSchema, db : Session = Depends(get_db), cur_user  = Depends (get_current_user)):
   """ Check the user is admin:
       find the member by email:
       add to organzations.. table...
   """
   member = db.query(Membership).filter(Membership.user_id == cur_user.get('user_id')).all()

   if not member:
      raise HTTPException(status_code = 401, details='Access declined!')
   
   # fetch user by email
   user = db.query(User).filter(User.email ==  member.email).all()
   print(user)

   # check if user is not already a member
   is_member = db.query(Membership).filter(Membership.user_id == user['id'] and Membership.role == 'member').all()
   if is_member:
      return {'message':'User is already a member'}

   # add to membership
   membership = Membership(
                           cur_user.get('user_id'),
                           org_id,
                           MemberRole.member
                           )   

   db.add(membership)
   db.commit()

   # return
   return {
    'message': 'Member added successfully',
    'member': {
        'email': user.email,
        'name': user.name,
        'role': MemberRole.member,
        'org_id': org_id
    }
}
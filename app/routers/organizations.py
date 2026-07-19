"""
   Create Organizations:
   Invite Members:


"""

from fastapi import APIRouter,HTTPException,Depends,Request
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole
from app.services.rate_limiting_service import checkRateLimit

org_router = APIRouter()


@org_router.post('/organization')
def create_organization(org_name : OrganizationForm, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):
   # authentications layer

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
async def invite_members(request:Request,org_id: int, invite: AddMemberSchema, db: Session = Depends(get_db), cur_user = Depends(get_current_user)):
      # RATE LIMIT
    redis = request.app.state.redis
    await checkRateLimit(redis,user_id=cur_user.get('user_id'))

    # check for org 
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404,detail='Organization not found!')
    
    # check current user is admin of this org
    admin_check = db.query(Membership).filter(
        Membership.user_id == cur_user.get('user_id'),
        Membership.org_id == org_id,
        Membership.role == MemberRole.admin
    ).first()
    
    if not admin_check:
        raise HTTPException(status_code=403, detail='Admin access required')
    
    # find user by email
    user = db.query(User).filter(User.email == invite.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # check not already a member
    is_member = db.query(Membership).filter(
        Membership.user_id == user.id,
        Membership.org_id == org_id
    ).first()
    
    if is_member:
        return {'message': 'User is already a member'}
    
    # add to membership
    new_membership = Membership(
        user_id=user.id,
        org_id=org_id,
        role=MemberRole.member
    )
    db.add(new_membership)
    db.commit()


    # Notifiy User that he has been added to the org membership
    manager = request.app.state.manager
    await manager.send_text_message(user_id=new_membership.user_id,message=f'You are now a member of {org.name}.')
    
    return {
        'message': 'Member added successfully',
        'member': {
            'email': user.email,
            'name': user.name,
            'role': MemberRole.member,
            'org_id': org_id
        }
    }


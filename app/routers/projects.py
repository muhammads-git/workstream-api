from fastapi import APIRouter,HTTPException,Depends
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole,Project
from app.schema import ProjectCreate


pro_router = APIRouter()


@pro_router.post('/projects')
def create_project(project : ProjectCreate, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):

   is_admin_or_member = db.query(Membership.user_id == cur_user.get('user_id'),
                                 Membership.role.in_([MemberRole.admin, MemberRole.manager])) 
   
   if not is_admin_or_member:
      raise HTTPException(status_code=403, detail='Access denied!')
   
   new_project = Project(title=project.title,
                         org_id=project.org_id,
                         created_by = cur_user.get('user_id'))
   
   db.add(new_project)
   db.commit()

   return {
    'message': 'Project created',
    'project': {
        'id': new_project.id,
        'title': new_project.title,
        'org_id': new_project.org_id,
        'created_by': cur_user.get('username'),
        'created_at': new_project.created_at
    }
}   


@pro_router.get('/projects/{org_id}')
def get_projects(org_id : int, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):

   # check authorization
   is_member = db.query(Membership).filter(Membership.user_id == cur_user.get('user_id'),
                                          Membership.org_id ==  org_id,
                                          Membership.role.in_([MemberRole.admin, MemberRole.manager, MemberRole.member])).first()
   if not is_member:
      raise HTTPException(status_code=403,detail='Access denied!')
   
   projects = db.query(Project).all()

   if not projects:
      return {
         'message':'Empty!'
      }
   #  clean data before rendering
   return {
    'projects': [
        {
            'id': p.id,
            'title': p.title,
            'org_id': p.org_id,
            'created_by': p.created_by,
            'created_at': p.created_at
        }
        for p in projects
    ]
}



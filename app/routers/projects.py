from fastapi import APIRouter,HTTPException,Depends,Request
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole,Project
from app.schema import ProjectCreate
import json

pro_router = APIRouter()


@pro_router.post('/projects')
async def create_project(request:Request,project : ProjectCreate, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):

   is_admin_or_member = db.query(Membership.user_id == cur_user.get('user_id'),
                                 Membership.role.in_([MemberRole.admin, MemberRole.manager])) 
   
   if not is_admin_or_member:
      raise HTTPException(status_code=403, detail='Access denied!')
   
   new_project = Project(title=project.title,
                         org_id=project.org_id,
                         created_by = cur_user.get('user_id'))
   
   db.add(new_project)
   db.commit()
   # delete cached projects:
   redis = request.app.state.redis
   await redis.delete(f'projects:{new_project.org_id}')


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
async def get_projects(request: Request, org_id: int, db: Session = Depends(get_db), cur_user = Depends(get_current_user)):

    # authorization
    is_member = db.query(Membership).filter(
        Membership.user_id == cur_user.get('user_id'),
        Membership.org_id == org_id,
        Membership.role.in_([MemberRole.admin, MemberRole.manager, MemberRole.member])
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail='Access denied!')

    # cache hit
    redis = request.app.state.redis
    cached = await redis.get(f'projects:{org_id}')
    if cached:
        return {'projects': json.loads(cached)}

    # cache miss — hit DB
    projects = db.query(Project).filter(Project.org_id == org_id).all()

    if not projects:
        return {'message': 'No projects found'}

    # serialize manually — datetime not JSON serializable
    data = [
        {
            'id': p.id,
            'title': p.title,
            'org_id': p.org_id,
            'created_by': p.created_by,
            'created_at': p.created_at.isoformat()
        }
        for p in projects
    ]

    # store in cache
    await redis.setex(f'projects:{org_id}', 300, json.dumps(data))

    return {'projects': data}

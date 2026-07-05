from fastapi import APIRouter,HTTPException,Depends
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole,Project,Task,TaskPriority,TaskStatus
from app.schema import TaskCreate
from datetime import datetime, timezone

task_router = APIRouter()


@task_router.post('/tasks')
def create_task(task : TaskCreate, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):
   # verify current user is admin or member or manager of the org

   org_id = db.query(Project.org_id).filter(Project.id == task.project_id).scalar()

   if not org_id:
    raise HTTPException(status_code=404, detail='Project not found')

   is_member_admin_manager = db.query(Membership).filter(
            Membership.user_id == cur_user.get('user_id'),
            Membership.org_id == org_id,
            Membership.role.in_([MemberRole.admin, MemberRole.manager])
   ).first()

   if not is_member_admin_manager:
      raise HTTPException(status_code=403,detail='Access denied!')
   

   # check past deadlines
   if task.deadline < datetime.now(timezone.utc):
     raise HTTPException(status_code=400, detail='Deadline cannot be in the past')
   
   # insert into tasks
   new_task = Task(project_id=task.project_id,
                   title=task.title,
                   priority=task.priority,
                   deadline=task.deadline)
   
   # add 
   db.add(new_task)
   db.commit()
   db.refresh(new_task)


   return {'message':'Task created!','details':{
      'id':new_task.id,
      'title':new_task.title,
      'project_id':new_task.project_id,
      'priority':new_task.priority,
      'deadline':new_task.deadline
   }}


from fastapi import APIRouter,HTTPException,Depends,Request
from app.schema import OrganizationForm,AddMemberSchema
from app.database import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.services.auth_services import get_current_user
from app.models import User,Organization,Membership,MemberRole,Project,Task,TaskPriority,TaskStatus,Assignment,Notification,NotificationType
from app.schema import TaskCreate,TaskAssign
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



@task_router.post('/tasks/{task_id}/assign')
async def assing_task(request:Request, task_assign : TaskAssign,task_id : int, db : Session = Depends(get_db), cur_user = Depends(get_current_user)):
   
   # fetch org_id from the task chain

   # Task -> Project -> Organization
   project_id = db.query(Task.project_id).filter(Task.id == task_id).scalar()

   if not project_id:
     raise HTTPException(status_code=404,detail='Project not found!')
   # org_id
   org_id = db.query(Project.org_id).filter(Project.id == project_id).scalar()
   
   if not org_id:
     raise HTTPException(status_code=404,detail='Organization not found!')
   # uthorization check
   is_admin_manager = db.query(Membership).filter(Membership.user_id == cur_user.get('user_id'),
                                                  Membership.org_id == org_id,
                                                  Membership.role.in_([MemberRole.manager,MemberRole.admin])).first()
   
   if not is_admin_manager:
     raise HTTPException(status_code=403,detail='Access denied!')
   
   # # check the user we are assigning task to is member of the org

   is_member = db.query(Membership).filter(Membership.user_id == task_assign.user_id,
                               Membership.org_id == org_id).first()
   
   if not is_member:
     raise HTTPException(status_code=403,detail='User is not the member of this organization!')
   
   
   # assign task to the user
   # ASSIGNMENT
   new_assignment = Assignment(user_id=task_assign.user_id,
                               task_id=task_id,
                               assigned_by=cur_user.get('user_id'))


   # Notifications to user
   new_notification = Notification(user_id=task_assign.user_id,task_id=task_id,
                                   message=f'You have been assigned a task by {cur_user.get('username')}',
                                   type=NotificationType.task_assigned)
   
   # assignement
   db.add(new_assignment)
   # notification
   db.add(new_notification)
   db.commit()

   # PUSH TO WEBSOCKETS
   manager = request.app.state.manager
   print(f'Task manager is {id(manager)}')
   await manager.send_text_message(user_id=task_assign.user_id,
                                   message=new_notification.message)

   return {
     'message':'Task Assigned.','details':{
       'task_id':new_assignment.id,
       'assigned_to':task_assign.user_id,
       'assigned_by':cur_user.get('username'),

     }
   }


   
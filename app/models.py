from app.database import BASE
from sqlalchemy import String,Column, DateTime,Integer,ForeignKey,Enum,Text,Boolean
import enum
from datetime import timezone, datetime


class User(BASE):
   __tablename__= "users"

   id = Column(Integer,primary_key=True,autoincrement=True)
   email = Column(String, unique=True, nullable=False)
   password = Column(String, nullable=False)
   name = Column(String, nullable=False)

class Organization(BASE):
   __tablename__= "organizations"

   id = Column(Integer,primary_key=True,autoincrement=True)
   name=Column(String,unique=True)
   created_at=Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
   created_by= Column(Integer, ForeignKey('users.id'))

class Project(BASE):
   __tablename__="projects"

   id = Column(Integer,primary_key=True,autoincrement=True)
   title = Column(String)
   org_id = Column(Integer,ForeignKey('organizations.id'))
   created_by = Column(Integer,ForeignKey('users.id'))
   created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

# Enum for priority
class TaskStatus(enum.Enum):
   todo = "todo"
   in_progress = "in_progress"
   review = "review"
   done = "done"
# Enum for priority
class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Task(BASE):
   __tablename__="tasks"

   id = Column(Integer,primary_key=True,autoincrement=True)
   project_id = Column(Integer,ForeignKey('projects.id'))
   title= Column(String)
   status = Column(Enum(TaskStatus), default=TaskStatus.todo)
   priority= Column(Enum(TaskPriority),default=TaskPriority.medium)
   created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
   deadline=Column(DateTime(timezone=True), nullable=True)
# role 
class MemberRole(enum.Enum):
   admin = "admin"
   manager="manager"
   viewer="viewer"
   member="member"

class Membership(BASE):
   __tablename__ = "memberships"
   id = Column(Integer,primary_key=True,autoincrement=True)
   user_id=Column(Integer,ForeignKey("users.id"))
   org_id =Column(Integer,ForeignKey("organizations.id"))
   role=Column(Enum(MemberRole),default=MemberRole.member)
   joined_at=Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))


class Assignment(BASE):
   __tablename__="assignments"

   id = Column(Integer, primary_key=True, autoincrement=True)
   user_id = Column(Integer, ForeignKey("users.id")) 
   task_id =Column(Integer, ForeignKey("tasks.id"))
   assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
   assigned_by = Column(Integer, ForeignKey("users.id"))

# type 
class NotificationType(enum.Enum):
    task_assigned = "task_assigned"
    deadline_approaching = "deadline_approaching"
    comment_added = "comment_added"
    status_changed = "status_changed"

class Notification(BASE):
   __tablename__ = "notifications"
   
   id = Column(Integer, primary_key=True, autoincrement=True)
   message = Column(Text)
   read = Column(Boolean, default=False, server_default='false', nullable=False)
   user_id = Column(Integer, ForeignKey("users.id"))
   task_id = Column(Integer, ForeignKey("tasks.id"))
   type = Column(Enum(NotificationType), nullable=False)


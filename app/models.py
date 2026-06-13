from app.database import BASE
from sqlalchemy import String,Column, DateTime,Integer,ForeignKey


class USER(BASE):
   __tablename__= "users"

   id = Column(Integer,primary_key=True,autoincrement=True)
   name = Column(String)
   email = Column(String)
   password = Column(String)


class ORGANIZATION(BASE):
   __tablename__= "organizations"

   id = Column(Integer,primary_key=True,autoincrement=True)
   name=Column(String,unique=True)
   created_at=Column(DateTime)
   created_by= Column(Integer, ForeignKey('users.id'))



class PROJECT(BASE):
   __tablename__="projects"

   id = Column(Integer,primary_key=True,autoincrement=True)
   title = Column(String)
   org_id = Column(Integer,ForeignKey('organizations.id'))
   created_by = Column(Integer,ForeignKey('users.id'))


class TASK(BASE):
   __tablename__="tasks"

   id = Column(Integer,primary_key=True,autoincrement=True)
   project_id=Column(Integer,ForeignKey('projects.id'))
   title=Column(String)
   status=

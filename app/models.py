from app.database import BASE
from sqlalchemy import String,Column, DateTime,Integer


class USER(BASE):
   __tablename__= "users"

   id = Column(Integer,primary_key=True,autoincrement=True)
   name = Column(String)
   email = Column(String)
   password = Column(String)

   
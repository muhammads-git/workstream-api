from fastapi import FastApi
from app.models import BASE
from app.database import engine
from app.auths.auth import auths_router

# create instance 
app = FastApi("NexusAPI")
# create models
BASE.metadata.create_all(bind=engine)
# attach routers
app.include_router(auths_router,prefix='/auth',tags=['auth'])


@app.get('/')
def root():
    return {'message': 'API running'}




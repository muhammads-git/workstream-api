from fastapi import FastAPI
from app.models import BASE
from app.database import engine
from app.auths.auth import auths_router
from app.routers.organizations import org_router
from app.routers.projects import pro_router
from app.routers.tasks import task_router

# create instance 
app = FastAPI(title="NexusAPI")
# create models
BASE.metadata.create_all(bind=engine)
# attach routers
app.include_router(auths_router,prefix='/auth',tags=['auth'])
app.include_router(org_router,prefix='/v1',tags=['org'])
app.include_router(pro_router,prefix='/v1',tags=['projects'])
app.include_router(task_router,prefix='/v1',tags=['tasks'])

@app.get('/')
def root():
    return {'message': 'API running'}




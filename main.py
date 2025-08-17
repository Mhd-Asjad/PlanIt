from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.auth import router as auth_router 
from api.routers.task import  router as task_router

app = FastAPI()

origins = ["http://localhost:5173" , "https://planit-scheduler.vercel.app" , "https://api.planit.publicvm.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router , prefix="/api/user", tags=["User"])
app.include_router(task_router , prefix="/api/task", tags=["Tasks"])
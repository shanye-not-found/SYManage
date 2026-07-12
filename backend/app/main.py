from fastapi import FastAPI
from sqlmodel import Session
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.users.router import user_router
from app.users.service import init_superadmin


app = FastAPI(title=settings.APP_NAME)

# cross origin resourse sharing middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    with Session(engine) as session:
        init_superadmin(session)


app.include_router(user_router)

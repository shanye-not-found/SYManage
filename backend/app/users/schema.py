from sqlmodel import SQLModel
import uuid
from app.users.model import Permission
from datetime import datetime

class UserAddWhiteList(SQLModel):
    username: str
    email: str
    permission: Permission
    wechat_account: str
    retired: bool = False
    
class UserCreate(SQLModel):
    email: str
    password: str
 
class UserLogin(SQLModel):
    email: str  
    password: str
    remember_me: bool = False
    
class UserPublic(SQLModel):
    id: uuid.UUID
    email: str
    permission: Permission
    username: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class WhitelistPublic(SQLModel):
    id: uuid.UUID
    username: str
    email: str
    permission: Permission
    wechat_account: str
    retired: bool
    created_at: datetime
    retired_at: datetime | None
    retired_description: str | None = None
    highest_permission: Permission
    
class WhiteListCreate(SQLModel):
    username: str
    email: str
    permission: Permission
    wechat_account: str
    retired: bool = False

    
# class UserPublicFull(SQLModel):
#     id: uuid.UUID
#     email: str
from sqlmodel import SQLModel
import uuid
from app.users.model import Permission

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
    working_year: int
    
class WhiteListCreate(SQLModel):
    username: str
    email: str
    permission: Permission
    wechat_account: str
    retired: bool = False
    working_year: int
    
# class UserPublicFull(SQLModel):
#     id: uuid.UUID
#     email: str
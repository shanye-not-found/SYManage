import uuid
import datetime
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship

class Permission(str,Enum):
    superadmin = "superadmin"
    president = "president"
    vice_president = "vice_president"
    cocktail_minister = "cocktail_minister"
    tea_minister = "tea_minister"
    treasurer = "treasurer"
    manager = "manager"  
   
def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def get_current_year_int() -> int:
    return datetime.datetime.now().year

class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    email: str = Field(unique=True)
    hashed_password: str = Field(nullable=False)
    whitelist_id: uuid.UUID = Field(foreign_key="white_list.id",nullable=False)
    whitelist: "WhiteList" = Relationship(back_populates="user") # type: ignore

    created_at: datetime.datetime = Field(default_factory=utc_now)
    updated_at: datetime.datetime = Field(default_factory=utc_now)

class WhiteList(SQLModel, table=True):
    __tablename__ = "white_list" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    email: str = Field(unique=True,index=True)
    username: str = Field(unique=True)
    permission: Permission = Field(nullable=False)
    wechat_account: str = Field(nullable=False)
    retired: bool = Field(default=False)
    user: User | None = Relationship(back_populates="whitelist")
    working_year: int = Field(nullable=True, default_factory=get_current_year_int) # 在前端传默认值，默认当前年份
    # 后续如果需要，可以再加 retired_year 记录退休年份

    
    


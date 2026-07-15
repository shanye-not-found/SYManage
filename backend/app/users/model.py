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
    tea_manager = "tea_manager"  
    bar_manager = "bar_manager"  
   
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
    username: str = Field(unique=True) #现在做的所有逻辑都是unique=True，如果后面加上了特殊的身份识别手段，要在依赖函数中改
    permission: Permission = Field(nullable=False)
    wechat_account: str = Field(nullable=False)
    user: User | None = Relationship(back_populates="whitelist")
    
    retired: bool = Field(default=False)
    created_at: datetime.datetime = Field(nullable = False, default_factory=utc_now)
    retired_at: datetime.datetime = Field(nullable=True, default=None) # 退休时间，可以为空
    retired_description: str = Field(nullable=True, default=None) 
    highest_permission: Permission = Field(nullable=False, default=Permission.cocktail_minister)
    
    # 后续如果需要，可以再加 retired_year 记录退休年份

    
    


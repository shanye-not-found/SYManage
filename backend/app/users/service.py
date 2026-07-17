import jwt
from sqlmodel import Session, select

from app.users.model import User, WhiteList, Permission
from app.users.schema import UserCreate, WhiteListCreate, WhitelistPublic
from app.users.security import hash_password, verify_password, decode_access_token
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.db.session import get_db

def get_whitelist_email(session: Session, email: str) -> WhiteList | None:
    statement = select(WhiteList).where(WhiteList.email == email) #sql语句
    return session.exec(statement).first() #实际执行

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def whitelist_to_public(whitelist: WhiteList) -> WhitelistPublic:
    return WhitelistPublic(
        id=whitelist.id,
        email=whitelist.email,
        username=whitelist.username,
        permission=whitelist.permission,
        wechat_account=whitelist.wechat_account,
        retired=whitelist.retired,
        created_at=whitelist.created_at,
        retired_at=whitelist.retired_at,
        retired_description=whitelist.retired_description,
        highest_permission=whitelist.highest_permission
    )


def create_user(session: Session, user: UserCreate) -> User:
    email = user.email
    whitelist = get_whitelist_email(session, email)
    if not whitelist:
        raise ValueError("Whitelist email not found")

    existing_user = get_user_by_email(session, user.email)
    if existing_user:
        raise ValueError("User already exists")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password,whitelist_id=whitelist.id)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
    

def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
    # superadmin可以直接使用superadmin作为邮箱字段登陆
    
def init_superadmin(session: Session):
    superadmin_email = settings.SUPERADMIN_EMAIL
    superadmin_password = settings.SUPERADMIN_PASSWORD
    statement = select(WhiteList).where(WhiteList.email == superadmin_email)
    superadmin_whitelist = session.exec(statement).first()
    if not superadmin_whitelist:
        add_manager_into_whitelist(session, WhiteListCreate(username=settings.SUPERADMIN_USERNAME, email=settings.SUPERADMIN_EMAIL
                                                            , permission=Permission.superadmin,wechat_account=settings.SUPERADMIN_WECHAT_ACCOUNT
                                                            , retired=False))
    user = get_user_by_email(session, superadmin_email)   
    if not user:
        user = create_user(session, UserCreate(email=superadmin_email, password=superadmin_password))
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
def get_current_user(session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        email= decode_access_token(token)
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user = get_user_by_email(session, email) 
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

def get_whitelist_all(session: Session) -> list[WhiteList]:
    statement = select(WhiteList)
    return list(session.exec(statement).all())
    
def add_manager_into_whitelist(session: Session, whitelist: WhiteListCreate) -> WhiteList:
    email = whitelist.email
    existing_whitelist = get_whitelist_email(session, email)
    if existing_whitelist:
        raise ValueError("This manager has already exists in whitelist")
    
    new_whitelist = WhiteList(email=whitelist.email, username=whitelist.username, 
                              permission=whitelist.permission,wechat_account=whitelist.wechat_account, 
                              retired=whitelist.retired)
    session.add(new_whitelist)
    session.commit()
    session.refresh(new_whitelist)
    return new_whitelist

def add_whitelist_all(session: Session, whitelist_json: list[WhiteListCreate]) -> list[WhiteList]:
    
    email_set = set()
    usernames_set = set()
    count = 1
    count_exist = 1
    for whitelist in whitelist_json:
        if whitelist.email in email_set:
            raise ValueError(f"Duplicate email in the batch: Batch Number {count}, email is {whitelist.email}")
        if whitelist.username in usernames_set:
            raise ValueError(f"Duplicate username in the batch: Batch Number {count}, username is {whitelist.username}")
        email_set.add(whitelist.email)
        usernames_set.add(whitelist.username)
        count += 1
        
    for whitelist in whitelist_json:
        email = whitelist.email
        permission = whitelist.permission
        existing_whitelist = get_whitelist_email(session, email)
        if existing_whitelist:
            raise ValueError("Number {count_exist} manager has already exists in whitelist.")
        if permission == Permission.superadmin or permission == Permission.president or permission == Permission.treasurer:
            raise ValueError(f"Invalid Permission: Number {count_exist} manager.")
        count_exist += 1   
        
    new_whitelists = [WhiteList(email=whitelist.email, username=whitelist.username,
                                    permission=whitelist.permission,wechat_account=whitelist.wechat_account,
                                    retired=whitelist.retired)
                        for whitelist in whitelist_json]
    session.add_all(new_whitelists)
    session.commit()
       
    for whitelist in new_whitelists:
        session.refresh(whitelist)
    return new_whitelists
            
            
        
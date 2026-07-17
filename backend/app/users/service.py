import jwt
from sqlmodel import Session, select

from app.users.model import Status, User, WhiteList, Permission, HandoverTable, utc_now
from app.users.schema import UserCreate, WhiteListCreate, WhitelistPublic, HandoverTableCreate,  PermissionUpdate
from app.users.security import gen_handover_token, hash_password, verify_password, decode_access_token
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
            raise ValueError(f"Number {count_exist} manager has already exists in whitelist.")
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

def calculate_highest_permission(permission: Permission, highest_permission: Permission) -> Permission:

    permission_levels = {
        Permission.superadmin: 1,
        Permission.president: 2,
        Permission.vice_president: 3,
        Permission.treasurer: 4,
        Permission.cocktail_minister: 4,
        Permission.tea_minister: 4,
        Permission.tea_manager: 5,
        Permission.bar_manager: 5,
    }
    
    # 比较并返回等级更高的（数字更小的）
    if permission_levels[permission] < permission_levels[highest_permission]:
        return permission
    else:
        return highest_permission
    
def get_handover_record(session: Session, token: str) -> HandoverTable | None:
    statement = select(HandoverTable).where(HandoverTable.token == token).with_for_update() #加锁
    return session.exec(statement).first()
           
def create_handover_record(session: Session, handover_table: HandoverTableCreate) -> HandoverTable:   
    to_email = handover_table.to_user_email         
    to_user = get_user_by_email(session, to_email)
    if not to_user: 
        raise ValueError("The user does not exist")
    
    token = gen_handover_token()
    while get_handover_record(session, token):
        token = gen_handover_token()
        
    new_handover_record = HandoverTable(token=token,
                                        from_user_email=handover_table.from_user_email, 
                                        self_permission=handover_table.self_permission, 
                                        to_user_email=to_email, 
                                        target_permission=handover_table.target_permission)
    session.add(new_handover_record)
    session.commit()
    session.refresh(new_handover_record)
    return new_handover_record
    
def update_permission(session: Session, update_table: PermissionUpdate):
    token = update_table.token
    table = get_handover_record(session, token)
    if not table:
        raise ValueError("The token is invalid")
    
    if table.status != "pending":
        raise ValueError("The token is not pending")
    
    if table.expired_at < utc_now():
        raise ValueError("The token is expired")
    
    if table.to_user_email != update_table.low_user_email:
        raise ValueError("The target user is not the same")
    
    high_whitelist = get_whitelist_email(session, table.from_user_email)
    low_whitelist = get_whitelist_email(session, update_table.low_user_email)
    if high_whitelist and low_whitelist:
        high_whitelist.highest_permission = calculate_highest_permission(table.self_permission, high_whitelist.highest_permission)
        low_whitelist.highest_permission = calculate_highest_permission(table.target_permission, low_whitelist.highest_permission)
        high_whitelist.permission = table.self_permission
        low_whitelist.permission = table.target_permission
        table.status = Status.completed
        session.add(high_whitelist)
        session.add(low_whitelist)
        session.add(table)
        session.commit()
        session.refresh(table)
        session.refresh(high_whitelist)
        session.refresh(low_whitelist)
        return table
        

import jwt
from sqlmodel import Session, select

from app.users.model import Status, User, WhiteList, Permission, HandoverTable, utc_now
from app.users.schema import HandoverTablePublic, PermissionUpdatePublic, UserCreate, WhiteListCreate, WhitelistPublic, HandoverTableCreate,  PermissionUpdate
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
        whitelist = WhiteListCreate(username=settings.SUPERADMIN_USERNAME, email=settings.SUPERADMIN_EMAIL
                                    , permission=Permission.superadmin,wechat_account=settings.SUPERADMIN_WECHAT_ACCOUNT
                                    , retired=False)
 
        new_whitelist = WhiteList(email=whitelist.email, username=whitelist.username, 
                                permission=whitelist.permission,wechat_account=whitelist.wechat_account, 
                                retired=whitelist.retired)
        session.add(new_whitelist)
        session.commit()
        session.refresh(new_whitelist)

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
    
    if whitelist.permission != Permission.tea_manager and whitelist.permission != Permission.bar_manager:
        raise ValueError("Invalid Permission")
    
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
        if permission != Permission.tea_manager and permission != Permission.bar_manager:
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

def get_record_by_email(session: Session, email: str) -> list[HandoverTable] | None:
    statement = select(HandoverTable).where(HandoverTable.from_user_email == email).with_for_update() #加锁
    return list(session.exec(statement).all())

def get_whitelist_by_permission(session: Session, permission: Permission) -> WhiteList | None:
    statement = select(WhiteList).where(WhiteList.permission == permission)
    return session.exec(statement).first()
    
    # 这是create_handover_record的状态函数
def get_handover_state(session: Session, target_permission: Permission, from_user: WhiteList) -> int:
    if from_user.permission == Permission.superadmin:
        if target_permission == Permission.president or target_permission == Permission.treasurer:
            return 1 #不用降自身，需要直接找到permission==target_permission的manager，同时降权和升权，系统中如果没有那就直接加上，需要生成token
        elif target_permission == Permission.bar_manager or target_permission == Permission.tea_manager:
            return 9999 #不用降自身,基本用不到
        else:
            return 2 #需要直接找到permission==target_permission的manager，同时降权和升权，系统中如果没有那就直接加上，不需要生成token
    elif from_user.permission == Permission.president:
        if target_permission == Permission.president:
            return 3 #降自身并升权，需要生成token
        elif target_permission == Permission.bar_manager or target_permission == Permission.tea_manager:
            return 9999 #不用降自身,基本用不到
        else:
            return 2 #不用降自身，需要直接找到permission==target_permission的manager，同时降权和升权，系统中如果没有那就直接加上，不需要生成token
    elif from_user.permission == Permission.treasurer:
        if target_permission == Permission.treasurer:
            return 3 #降自身并升权，需要生成token
        else:
            return 4 #deny
    else:
        return 4 #deny

# 如果不用降自身且不用token可以立即执行，但凡有一个就要直接生成表    
def create_handover_record(session: Session, handover_table: HandoverTableCreate, self_email: str) -> HandoverTablePublic | PermissionUpdatePublic:      
    to_user = get_user_by_email(session, handover_table.to_user_email)
    from_user = get_whitelist_email(session, handover_table.from_user_email)
    
    if not to_user: 
        raise ValueError("The user does not exist")
    
    if not from_user:
        raise ValueError("The manager does not exist")
    
    state = get_handover_state(session, handover_table.target_permission, from_user)
    
    if self_email != handover_table.from_user_email:
        raise ValueError("Permission error")
    
    if handover_table.target_permission == Permission.superadmin:
        raise ValueError("Fork!!! You are not allowed to do this!")
    
    if handover_table.from_user_email == handover_table.to_user_email:
        raise ValueError("Self handover is not allowed")
    
    
    if state == 2:
        hwl = get_whitelist_by_permission(session, handover_table.target_permission)
        if hwl:
            lwl = get_whitelist_email(session, handover_table.to_user_email)
            if not lwl: 
               raise ValueError("The target user does not exist")
            if handover_table.self_permission != Permission.bar_manager and handover_table.self_permission != Permission.tea_manager:
                raise ValueError("Permission error")
            hwl.permission = handover_table.self_permission
            lwl.permission = handover_table.target_permission
            lwl.highest_permission = calculate_highest_permission(handover_table.target_permission, lwl.highest_permission)
            session.add(hwl)
            session.add(lwl)
            session.commit()
            session.refresh(lwl)
            session.refresh(hwl)
            return PermissionUpdatePublic(high_username=hwl.username, low_username=lwl.username, target_permission=handover_table.target_permission,self_permission=handover_table.self_permission)
        else:
            lwl = get_whitelist_email(session, handover_table.to_user_email)
            if not lwl: 
               raise ValueError("The target user does not exist")
            lwl.permission = handover_table.target_permission
            lwl.highest_permission = calculate_highest_permission(handover_table.target_permission, lwl.highest_permission)
            session.add(lwl)
            session.commit()
            session.refresh(lwl)
            
            return PermissionUpdatePublic(high_username=None, low_username=lwl.username, target_permission=handover_table.target_permission,self_permission=handover_table.self_permission)


    elif state == 9999:
        lwl = get_whitelist_email(session, handover_table.to_user_email)
        if not lwl: 
            raise ValueError("The target user does not exist")
        lwl.permission = handover_table.target_permission
        lwl.highest_permission = calculate_highest_permission(handover_table.target_permission, lwl.highest_permission)
        session.add(lwl)
        session.commit()
        session.refresh(lwl)
        
        return PermissionUpdatePublic(high_username=None, low_username=lwl.username, target_permission=handover_table.target_permission,self_permission=handover_table.self_permission)
        
        
        
    elif state == 4:
        raise ValueError("Permission error")
    else:
        lwl = get_whitelist_email(session, handover_table.to_user_email)
        if not lwl: 
            raise ValueError("The target user does not exist")
        token = gen_handover_token()
        while get_handover_record(session, token):
            token = gen_handover_token()
            
        new_handover_record = HandoverTable(token=token,
                                            from_user_email=handover_table.from_user_email, 
                                            self_permission=handover_table.self_permission, 
                                            to_user_email=handover_table.to_user_email, 
                                            target_permission=handover_table.target_permission)
        session.add(new_handover_record)
        session.commit()
        session.refresh(new_handover_record)
        return HandoverTablePublic(token=token, low_username=lwl.username, target_permission=handover_table.target_permission,self_permission=handover_table.self_permission)
    # 能进到第二步的只有1 3
def update_permission(session: Session, update_table: PermissionUpdate) -> PermissionUpdatePublic:
    token = update_table.token
    table = get_handover_record(session, token)
    if not table:
        raise ValueError("The token is invalid")
    
    if table.status != Status.pending:
        raise ValueError("The token is not pending")
    
    if table.expired_at < utc_now():
        raise ValueError("The token is expired")
    
    if table.to_user_email != update_table.low_user_email:
        raise ValueError("The target user is not the same")
    
    whitelist = get_whitelist_email(session, table.from_user_email)  
    if not whitelist:
        raise ValueError("The target user does not exist")  
    
    state = get_handover_state(session, table.target_permission, whitelist)
    
    if state == 1:
        hwl = get_whitelist_by_permission(session, table.target_permission)
        lwl = get_whitelist_email(session, update_table.low_user_email)
        if not lwl: 
            raise ValueError("The target user does not exist")
        if hwl:
            if table.self_permission != Permission.bar_manager and table.self_permission != Permission.tea_manager:
                raise ValueError("Permission error")
            hwl.permission = table.self_permission
            lwl.permission = table.target_permission
            table.status = Status.completed
            tables = get_record_by_email(session, table.from_user_email)
            if tables: 
                for t in tables:
                    if t.status == Status.pending:
                        t.status = Status.cancelled
                        session.add(t)
            lwl.highest_permission = calculate_highest_permission(table.target_permission, lwl.highest_permission)
            session.add(hwl)
            session.add(lwl)
            session.add(table)
            session.commit()
            session.refresh(table)
            session.refresh(hwl)
            session.refresh(lwl)
            return PermissionUpdatePublic(high_username=hwl.username, low_username=lwl.username, target_permission=table.target_permission,self_permission=table.self_permission)
        else:
            lwl.permission = table.target_permission
            lwl.highest_permission = calculate_highest_permission(table.target_permission, lwl.highest_permission)
            table.status = Status.completed
            tables = get_record_by_email(session, table.from_user_email)
            if tables: 
                for t in tables:
                    if t.status == Status.pending:
                        t.status = Status.cancelled
                        session.add(t)
            session.add(lwl)
            session.add(table)
            session.commit()
            session.refresh(table)
            session.refresh(lwl)
            return PermissionUpdatePublic(high_username=None, low_username=lwl.username, target_permission=table.target_permission,self_permission=table.self_permission)
                
    elif state == 3:
        hwl = get_whitelist_email(session, table.from_user_email)
        lwl = get_whitelist_email(session, update_table.low_user_email)
        if hwl and lwl:
            if table.self_permission != Permission.bar_manager and table.self_permission != Permission.tea_manager:
                raise ValueError("Permission error")
            hwl.permission = table.self_permission
            lwl.permission = table.target_permission
            lwl.highest_permission = calculate_highest_permission(table.target_permission, lwl.highest_permission)
            table.status = Status.completed
            session.add(hwl)
            session.add(lwl)
            session.add(table)
            tables = get_record_by_email(session, table.from_user_email)
            if tables: 
                for t in tables:
                    if t.status == Status.pending:
                        t.status = Status.cancelled
                        session.add(t)
            session.commit()
            session.refresh(table)
            session.refresh(hwl)
            session.refresh(lwl)
            return PermissionUpdatePublic(high_username=hwl.username, low_username=lwl.username, target_permission=table.target_permission,self_permission=table.self_permission)
        else:
            raise ValueError("Invalid user")
    else:
        raise ValueError("Permission error")

 
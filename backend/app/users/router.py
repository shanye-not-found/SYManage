from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.db.session import get_db
from app.users.schema import HandoverTablePublic, HandoverTableCreate, PermissionUpdate, Token, UserCreate, UserLogin, UserPublic,WhitelistPublic,WhiteListCreate, PermissionUpdatePublic
from app.users.service import add_whitelist_all, create_user,add_manager_into_whitelist, whitelist_to_public
from app.users.model import User
from app.users.service import get_current_user, authenticate_user, get_whitelist_all, create_handover_record, update_permission
from app.users.model import Permission
from app.users.security import create_access_token
from app.dependencies import require_admin, require_handover_capable


user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/register", response_model=UserPublic)
def register_user(user: UserCreate, session: Session = Depends(get_db)) -> UserPublic:
    try:
        new_user = create_user(session, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return UserPublic(
        id=new_user.id,
        email=new_user.email,
        permission=new_user.whitelist.permission,
        username=new_user.whitelist.username,
    )
        
@user_router.post("/login", response_model=Token)
def login(self_user: UserLogin, session: Session = Depends(get_db)) -> Token:
    try:
        user = authenticate_user(session, self_user.email, self_user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(user.email)
    return Token(access_token=token, token_type="bearer")


@user_router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.email)
    return Token(access_token=token, token_type="bearer")
    
    
    
@user_router.get("/me", response_model=UserPublic)
def read_me(curr_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=curr_user.id,
        email=curr_user.email,
        permission=curr_user.whitelist.permission,
        username=curr_user.whitelist.username
    )    
    
@user_router.get("/whitelist", response_model=list[WhitelistPublic])
def get_whitelist(session: Session = Depends(get_db),curr_user: User = Depends(get_current_user) ) -> list[WhitelistPublic]:
    if curr_user:
        white_list = get_whitelist_all(session)
        return [whitelist_to_public(whitelist) for whitelist in white_list]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@user_router.post("/add_whitelist", response_model=WhitelistPublic)
def add_whitelist(
    whitelist_info: WhiteListCreate,
    curr_user: User = Depends(require_admin),
    session: Session = Depends(get_db)
) -> WhitelistPublic:
    try:
        new_whitelist = add_manager_into_whitelist(session, whitelist_info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return whitelist_to_public(new_whitelist)
            

@user_router.post("/add_whitelist_multiple", response_model=list[WhitelistPublic])
def add_whitelist_multiple(
    whitelist_info: list[WhiteListCreate],
    curr_user: User = Depends(require_admin),
    session: Session = Depends(get_db)
) -> list[WhitelistPublic]:
    try:
        new_whitelists = add_whitelist_all(session, whitelist_info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return [whitelist_to_public(new_whitelist) for new_whitelist in new_whitelists]
    
@user_router.post("/gen_handover_table", response_model=HandoverTablePublic | PermissionUpdatePublic)
def gen_handover_table(
    handover_table_info: HandoverTableCreate,
    curr_user: User = Depends(require_handover_capable),
    session: Session = Depends(get_db)
) -> HandoverTablePublic | PermissionUpdatePublic:
    # 财务只能交接给财务的特殊逻辑
    if curr_user.whitelist.permission == Permission.treasurer and handover_table_info.target_permission != Permission.treasurer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Treasurer can only handover to Treasurer")

    try:
        new_table = create_handover_record(session, handover_table_info, curr_user.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return new_table
               
@user_router.post("/handover_permission", response_model=PermissionUpdatePublic)
def handover_permission(
    update_table: PermissionUpdate,
    curr_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> PermissionUpdatePublic:
    # 只有降权方本人可以确认交接
    if curr_user.email != update_table.low_user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to handover permission")

    try:
        table = update_permission(session, update_table)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return table

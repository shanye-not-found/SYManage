from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.db.session import get_db
from app.users.schema import Token, UserCreate, UserLogin, UserPublic,WhitelistPublic,WhiteListCreate
from app.users.service import add_whitelist_all, create_user,add_manager_into_whitelist, whitelist_to_public
from app.users.model import User
from app.users.service import get_current_user, authenticate_user, get_whitelist_all
from app.users.model import Permission
from app.users.security import create_access_token


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
def get_whitelist(session: Session = Depends(get_db), curr_user: User = Depends(get_current_user)) -> list[WhitelistPublic]:
    if curr_user.whitelist.permission == Permission.superadmin or curr_user.whitelist.permission == Permission.president:
        white_list = get_whitelist_all(session)
        return [whitelist_to_public(whitelist) for whitelist in white_list]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access the whitelist")  # 没有权限访问白名单

@user_router.post("/add_whitelist", response_model=WhitelistPublic)
def add_whitelist(whitelist_info: WhiteListCreate,curr_user: User = Depends(get_current_user), session: Session = Depends(get_db)) -> WhitelistPublic:
    if curr_user.whitelist.permission == Permission.superadmin or curr_user.whitelist.permission == Permission.president:
        try:
            new_whitelist = add_manager_into_whitelist(session, whitelist_info)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        return whitelist_to_public(new_whitelist) 
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add a whitelist")  # 没有权限添加白名单
            

@user_router.post("/add_whitelist_multiple")
def add_whitelist_multiple(whitelist_info: list[WhiteListCreate],curr_user: User = Depends(get_current_user), session: Session = Depends(get_db)) -> list[WhitelistPublic]:
    if curr_user.whitelist.permission == Permission.superadmin or curr_user.whitelist.permission == Permission.president:
        try:
            new_whitelists = add_whitelist_all(session, whitelist_info)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return [whitelist_to_public(new_whitelist) for new_whitelist in new_whitelists]  # 返回添加的多个白名单信息
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add multiple whitelist")  # 没有权限添加多个白名单
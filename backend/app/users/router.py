from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.db.session import get_db
from app.users.schema import Token, UserCreate, UserLogin, UserPublic,WhitelistPublic,WhiteListCreate
from app.users.service import create_user,add_manager_into_whitelist
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
# 后面还要加改权限的api    
@user_router.post("/add_whitelist", response_model=WhitelistPublic)
def add_whitelist(whitelist_info: WhiteListCreate,curr_user: User = Depends(get_current_user), session: Session = Depends(get_db)) -> WhitelistPublic:
    self_whitelist = curr_user.whitelist
    if not self_whitelist:
        raise ValueError("Your whitelist not found")
    
    if self_whitelist.permission == Permission.superadmin or self_whitelist.permission == Permission.president:
        try:
            new_whitelist = add_manager_into_whitelist(session, whitelist_info)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        return WhitelistPublic(
            id=new_whitelist.id,
            username=new_whitelist.username,
            email=new_whitelist.email,
            permission=new_whitelist.permission,
            wechat_account=new_whitelist.wechat_account,
            retired=new_whitelist.retired,
            working_year=new_whitelist.working_year
        ) 
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add a whitelist")  # 没有权限添加白名单
    
        
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
        return [WhitelistPublic(
            id=whitelist.id,
            username=whitelist.username,
            email=whitelist.email,
            permission=whitelist.permission,
            wechat_account=whitelist.wechat_account,
            retired=whitelist.retired,
            working_year=whitelist.working_year
        ) for whitelist in white_list]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access the whitelist")  # 没有权限访问白名单

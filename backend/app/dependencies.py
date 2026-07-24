from fastapi import Depends, HTTPException, status
from app.users.model import User, Permission
from app.users.service import get_current_user


def require_permissions(*allowed_permissions: Permission):
    """
    工厂函数：返回一个依赖函数，检查当前用户是否拥有指定权限之一

    使用示例：
        @router.post("/admin-only")
        def admin_route(user: User = Depends(require_permissions(Permission.superadmin))):
            ...

        @router.post("/multi-permission")
        def multi_route(user: User = Depends(require_permissions(Permission.superadmin, Permission.president))):
            ...

    参数：
        *allowed_permissions: 允许的权限（一个或多个 Permission 枚举值）

    返回：
        依赖函数，如果权限不足会抛出 403 HTTPException
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permission = current_user.whitelist.permission

        if user_permission not in allowed_permissions:
            # 格式化权限列表用于错误消息
            allowed_str = ", ".join(p.value for p in allowed_permissions)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {allowed_str}, but you have: {user_permission.value}"
            )

        return current_user

    return permission_checker


# ===== 预定义的常用权限依赖 =====

def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """仅 superadmin 可访问"""
    if current_user.whitelist.permission != Permission.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin permission required"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """superadmin 或 president 可访问（管理员级别）"""
    allowed = [Permission.superadmin, Permission.president]
    if current_user.whitelist.permission not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required (superadmin or president)"
        )
    return current_user


def require_leadership(current_user: User = Depends(get_current_user)) -> User:
    """领导层可访问：superadmin, president, vice_president"""
    allowed = [Permission.superadmin, Permission.president, Permission.vice_president]
    if current_user.whitelist.permission not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Leadership permission required"
        )
    return current_user


def require_minister_or_above(current_user: User = Depends(get_current_user)) -> User:
    """部长及以上可访问（不包括 manager）"""
    allowed = [
        Permission.superadmin,
        Permission.president,
        Permission.vice_president,
        Permission.cocktail_minister,
        Permission.tea_minister,
        Permission.treasurer,
    ]
    if current_user.whitelist.permission not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Minister-level permission or above required"
        )
    return current_user


def require_handover_capable(current_user: User = Depends(get_current_user)) -> User:
    """可以发起交接的权限：superadmin, president, treasurer"""
    allowed = [Permission.superadmin, Permission.president, Permission.treasurer]
    if current_user.whitelist.permission not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin, president, or treasurer can initiate handover"
        )
    return current_user
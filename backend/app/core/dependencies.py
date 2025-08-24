"""
FastAPI認証依存関数
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from .auth import decode_access_token, get_user_by_id, require_admin_role


# ===================================================================
# JWT認証依存関数
# ===================================================================

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    現在ログイン中のユーザーを取得
    HttpOnly CookieまたはAuthorizationヘッダーからトークンを読み取り
    """
    # まずAuthorizationヘッダーを確認（API利用）
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # "Bearer "の後の部分を取得
    
    # Authorizationヘッダーがない場合はCookieから取得（ブラウザ利用）
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
        )
    
    # トークンデコード
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効な認証情報です",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証情報です",
        )
    
    # ユーザー取得
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """アクティブなユーザーのみ許可"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="非アクティブなユーザーです",
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """管理者権限が必要な場合"""
    require_admin_role(current_user)
    return current_user


# ===================================================================
# オプショナル認証依存関数
# ===================================================================

async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    オプショナルな現在ユーザー取得
    認証されていない場合はNoneを返す
    """
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None
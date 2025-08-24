"""
JWT認証とセキュリティ機能
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import User, UserRole
from ..schemas.auth import UserMe


# パスワードハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
SECRET_KEY = os.getenv("SECRET_KEY", "forex-dev-secret-key-2024-very-secure-local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7日間（HttpOnly Cookieなので長めに設定）


# ===================================================================
# パスワード関連ユーティリティ
# ===================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードハッシュ化"""
    return pwd_context.hash(password)


# ===================================================================
# JWT トークン関連
# ===================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWTアクセストークンを生成"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """JWTトークンをデコード"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています",
        )
    except (jwt.InvalidSignatureError, jwt.DecodeError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
        )


# ===================================================================
# ユーザー認証関連
# ===================================================================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """ユーザー認証（ユーザー名またはメールアドレス）"""
    # ユーザー名またはメールアドレスで検索
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    # 非アクティブユーザーチェック
    if not user.is_active:
        return None
    
    # パスワード検証
    if not verify_password(password, user.hashed_password):
        # ログイン失敗回数をインクリメント
        user.failed_login_attempts += 1
        user.last_failed_login_at = datetime.utcnow()
        
        # 5回失敗でアカウント無効化
        if user.failed_login_attempts >= 5:
            user.is_active = False
        
        db.commit()
        return None
    
    # ログイン成功時の処理
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """IDからユーザー取得"""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()

def create_user_token(user: User) -> str:
    """ユーザー用JWTトークン生成"""
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
    }
    return create_access_token(data=token_data)


# ===================================================================
# 権限チェック関連
# ===================================================================

def check_admin_role(current_user: User) -> bool:
    """管理者権限チェック"""
    return current_user.role == UserRole.ADMIN

def require_admin_role(current_user: User):
    """管理者権限必須チェック（例外発生）"""
    if not check_admin_role(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )

def check_user_access(current_user: User, target_user_id: int) -> bool:
    """ユーザーアクセス権限チェック（自分のデータまたは管理者）"""
    return current_user.id == target_user_id or current_user.role == UserRole.ADMIN


# ===================================================================
# ユーザー作成関連
# ===================================================================

def create_user(db: Session, username: str, email: str, password: str, 
                full_name: Optional[str] = None, role: UserRole = UserRole.USER) -> User:
    """新規ユーザー作成"""
    # 重複チェック
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このユーザー名は既に使用されています",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています",
            )
    
    # ハッシュ化されたパスワード
    hashed_password = get_password_hash(password)
    
    # 新規ユーザー作成
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True,
        is_verified=True,  # 簡単のため自動検証済み
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


# ===================================================================
# パスワード変更関連
# ===================================================================

def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """ユーザーパスワード変更"""
    # 現在のパスワード検証
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のパスワードが間違っています",
        )
    
    # 新しいパスワードをハッシュ化
    user.hashed_password = get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return True
"""
簡易認証ルーター（データベース不要版）
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Response, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["auth"])

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydanticモデル
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    username: str
    email: str
    full_name: str
    role: str

# メモリ内のデモユーザー（実際の本番環境ではデータベースを使用）
DEMO_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("password"),
        "role": "admin"
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "full_name": "Demo User",
        "hashed_password": pwd_context.hash("password"),
        "role": "user"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """ユーザー認証"""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークンを作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(user_credentials: UserLogin, response: Response):
    """ログインエンドポイント"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンを作成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # Cookieにトークンを設定
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    # フロントエンドが期待する形式でレスポンスを返す
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": user["username"],
            "email": user["email"],
            "fullName": user["full_name"],
            "role": user["role"],
            "isActive": True,
            "isVerified": True,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
    }

@router.post("/logout")
async def logout(response: Response):
    """ログアウトエンドポイント"""
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """現在のユーザー情報を取得"""
    # Cookieまたはヘッダーからトークンを取得
    if not authorization:
        # デモ用：認証なしでもデモユーザーを返す
        user = DEMO_USERS.get("admin")
        return {
            "id": 1,
            "username": user["username"],
            "email": user["email"],
            "fullName": user["full_name"],
            "role": user["role"],
            "isActive": True,
            "isVerified": True,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
    
    try:
        # Bearerトークンから実際のトークンを抽出
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = DEMO_USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": 1 if username == "admin" else 2,
        "username": user["username"],
        "email": user["email"],
        "fullName": user["full_name"],
        "role": user["role"],
        "isActive": True,
        "isVerified": True,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z"
    }

@router.get("/check")
async def check_auth():
    """認証システムの動作確認"""
    return {
        "status": "ok",
        "message": "Auth system is working",
        "demo_users": ["admin", "user"]
    }
"""
認証関連のPydanticスキーマ定義
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from ..models import UserRole


# ===================================================================
# ユーザー登録・ログイン用スキーマ
# ===================================================================

class UserRegister(BaseModel):
    """ユーザー登録リクエスト"""
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名（3-50文字）")
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, max_length=100, description="パスワード（8文字以上）")
    full_name: Optional[str] = Field(None, max_length=100, description="フルネーム")
    
    @validator('password')
    def validate_password(cls, v):
        """パスワード強度チェック"""
        if len(v) < 8:
            raise ValueError('パスワードは8文字以上である必要があります')
        
        # 数字、英字を含むかチェック
        has_digit = any(c.isdigit() for c in v)
        has_alpha = any(c.isalpha() for c in v)
        
        if not (has_digit and has_alpha):
            raise ValueError('パスワードは英字と数字を含む必要があります')
        
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """ユーザー名形式チェック"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('ユーザー名は英数字、アンダースコア、ハイフンのみ使用可能です')
        return v

class UserLogin(BaseModel):
    """ユーザーログインリクエスト"""
    username: str = Field(..., description="ユーザー名またはメールアドレス")
    password: str = Field(..., description="パスワード")

class PasswordChange(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str = Field(..., description="現在のパスワード")
    new_password: str = Field(..., min_length=8, max_length=100, description="新しいパスワード")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """新しいパスワード強度チェック"""
        if len(v) < 8:
            raise ValueError('新しいパスワードは8文字以上である必要があります')
        
        has_digit = any(c.isdigit() for c in v)
        has_alpha = any(c.isalpha() for c in v)
        
        if not (has_digit and has_alpha):
            raise ValueError('新しいパスワードは英字と数字を含む必要があります')
        
        return v


# ===================================================================
# ユーザー情報レスポンス用スキーマ
# ===================================================================

class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserMe(BaseModel):
    """現在のユーザー情報レスポンス（簡易版）"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ===================================================================
# 認証レスポンス用スキーマ
# ===================================================================

class LoginResponse(BaseModel):
    """ログインレスポンス"""
    message: str = "ログインが成功しました"
    user: UserMe

class LogoutResponse(BaseModel):
    """ログアウトレスポンス"""
    message: str = "ログアウトしました"

class RegisterResponse(BaseModel):
    """登録レスポンス"""
    message: str = "ユーザー登録が完了しました"
    user: UserMe

class PasswordChangeResponse(BaseModel):
    """パスワード変更レスポンス"""
    message: str = "パスワードが変更されました"


# ===================================================================
# エラーレスポンス用スキーマ
# ===================================================================

class AuthError(BaseModel):
    """認証エラーレスポンス"""
    detail: str
    error_type: str = "authentication_error"

class ValidationError(BaseModel):
    """バリデーションエラーレスポンス"""
    detail: str
    error_type: str = "validation_error"
"""
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ...database import get_db
from ...models import User
from ...schemas.auth import (
    UserRegister, UserLogin, PasswordChange, 
    LoginResponse, LogoutResponse, RegisterResponse, PasswordChangeResponse,
    UserMe, AuthError
)
from ...core.auth import (
    authenticate_user, create_user_token, create_user, change_user_password
)
from ...core.dependencies import get_current_active_user

router = APIRouter()


# ===================================================================
# ユーザー登録エンドポイント
# ===================================================================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    新規ユーザー登録
    
    - **username**: ユーザー名（3-50文字、英数字・アンダースコア・ハイフンのみ）
    - **email**: メールアドレス
    - **password**: パスワード（8文字以上、英字と数字を含む）
    - **full_name**: フルネーム（オプション）
    
    成功時、HttpOnly Cookieに認証トークンが設定されます。
    """
    try:
        # 新規ユーザー作成
        user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # JWTトークン生成
        access_token = create_user_token(user)
        
        # HttpOnly Cookieにトークン設定
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 7,  # 7日間
            httponly=True,
            secure=False,  # 開発環境用（本番ではTrue）
            samesite="lax"
        )
        
        user_me = UserMe.from_orm(user)
        return RegisterResponse(user=user_me)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー登録中にエラーが発生しました"
        )


# ===================================================================
# ログインエンドポイント
# ===================================================================

@router.post("/login", response_model=LoginResponse)
async def login_user(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    ユーザーログイン
    
    - **username**: ユーザー名またはメールアドレス
    - **password**: パスワード
    
    成功時、HttpOnly Cookieに認証トークンが設定されます。
    5回連続でログインに失敗すると、アカウントが無効化されます。
    """
    try:
        # ユーザー認証
        user = authenticate_user(
            db=db,
            username=user_credentials.username,
            password=user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザー名またはパスワードが間違っています",
            )
        
        # JWTトークン生成
        access_token = create_user_token(user)
        
        # HttpOnly Cookieにトークン設定
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 7,  # 7日間
            httponly=True,
            secure=False,  # 開発環境用（本番ではTrue）
            samesite="lax"
        )
        
        user_me = UserMe.from_orm(user)
        return LoginResponse(user=user_me)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログイン中にエラーが発生しました"
        )


# ===================================================================
# ログアウトエンドポイント
# ===================================================================

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(response: Response):
    """
    ユーザーログアウト
    
    HttpOnly Cookieのトークンを削除します。
    """
    try:
        # Cookieを削除
        response.delete_cookie(key="access_token", httponly=True, samesite="lax")
        
        return LogoutResponse()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログアウト中にエラーが発生しました"
        )


# ===================================================================
# 現在のユーザー情報取得エンドポイント
# ===================================================================

@router.get("/me", response_model=UserMe)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    現在ログイン中のユーザー情報を取得
    
    認証が必要です。
    """
    return UserMe.from_orm(current_user)


# ===================================================================
# パスワード変更エンドポイント
# ===================================================================

@router.put("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    パスワード変更
    
    - **current_password**: 現在のパスワード
    - **new_password**: 新しいパスワード（8文字以上、英字と数字を含む）
    
    認証が必要です。
    """
    try:
        # パスワード変更処理
        change_user_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return PasswordChangeResponse()
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="パスワード変更中にエラーが発生しました"
        )
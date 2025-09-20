"""
JWT认证模块
支持固定Token和JWT Token两种认证方式
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# 固定API Token配置
API_TOKEN = os.getenv("API_TOKEN", "mcu-copilot-2025-seed-token")

# HTTP Bearer认证
security = HTTPBearer()

class JWTAuth:
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """创建JWT访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def verify_api_token(token: str) -> bool:
        """验证固定API令牌"""
        return token == API_TOKEN

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    依赖项：验证用户身份
    支持两种认证方式：
    1. 固定API Token (用于种子用户)
    2. JWT Token (用于生成的动态token)
    """
    token = credentials.credentials

    # 首先尝试固定API Token认证
    if JWTAuth.verify_api_token(token):
        return {
            "user_type": "seed_user",
            "token_type": "api_token",
            "authenticated": True
        }

    # 然后尝试JWT Token认证
    payload = JWTAuth.verify_token(token)
    if payload:
        return {
            "user_type": payload.get("sub", "jwt_user"),
            "token_type": "jwt_token",
            "authenticated": True,
            "payload": payload
        }

    # 认证失败
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

def require_auth(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    认证装饰器：要求请求必须携带有效的认证令牌
    """
    if not current_user.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

# 可选的认证装饰器（用于不强制要求认证的端点）
def optional_auth(request: Request) -> Optional[Dict[str, Any]]:
    """
    可选认证：如果提供了认证信息则验证，否则返回None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    # 尝试固定API Token
    if JWTAuth.verify_api_token(token):
        return {
            "user_type": "seed_user",
            "token_type": "api_token",
            "authenticated": True
        }

    # 尝试JWT Token
    payload = JWTAuth.verify_token(token)
    if payload:
        return {
            "user_type": payload.get("sub", "jwt_user"),
            "token_type": "jwt_token",
            "authenticated": True,
            "payload": payload
        }

    return None
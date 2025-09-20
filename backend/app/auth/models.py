"""
认证相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any

class TokenRequest(BaseModel):
    """生成Token请求模型"""
    user_id: str
    purpose: Optional[str] = "api_access"

class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒数

class UserInfo(BaseModel):
    """用户信息模型"""
    user_type: str
    token_type: str
    authenticated: bool
    payload: Optional[Dict[str, Any]] = None

class AuthStatus(BaseModel):
    """认证状态响应模型"""
    authenticated: bool
    user_info: Optional[UserInfo] = None
    message: str
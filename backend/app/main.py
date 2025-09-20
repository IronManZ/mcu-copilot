from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models.mcu_models import (
    CompileRequest, CompileResponse,
    NlpToAssemblyRequest, NlpToAssemblyResponse,
    AssembleRequest, AssembleResponse,
    ZH5001CompileRequest, ZH5001CompileResponse,
    ZH5001ValidateRequest, ZH5001ValidateResponse,
    ZH5001InfoResponse
)
from app.auth.models import TokenRequest, TokenResponse, AuthStatus, UserInfo
from app.auth.jwt_auth import JWTAuth, require_auth, optional_auth
from app.services.nl_to_assembly import nl_to_assembly
from app.services.assembly_compiler import assembly_to_machine_code
from app.services.compiler.zh5001_service import zh5001_service
import os
from dotenv import load_dotenv

app = FastAPI()

# CORS 配置
# 从环境变量获取允许的源，如果未设置则使用开发模式配置
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
if ALLOWED_ORIGINS:
    # 生产环境：从环境变量读取允许的域名
    allowed_origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]
else:
    # 开发环境：允许本地开发端口
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# 生产环境配置
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    print("DEBUG MODE: Environment variables loaded")
    print("DEBUG QIANWEN_APIKEY:", os.environ.get("QIANWEN_APIKEY")[:10] + "..." if os.environ.get("QIANWEN_APIKEY") else "Not set")
    print("DEBUG GEMINI_APIKEY:", os.environ.get("GEMINI_APIKEY")[:10] + "..." if os.environ.get("GEMINI_APIKEY") else "Not set")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 认证相关端点
@app.post("/auth/token", response_model=TokenResponse)
def create_token(token_request: TokenRequest):
    """
    生成JWT访问令牌
    用于为特定用户生成动态token
    """
    try:
        # 创建token数据
        token_data = {
            "sub": token_request.user_id,
            "purpose": token_request.purpose
        }

        # 生成JWT token
        access_token = JWTAuth.create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=24 * 3600  # 24小时，以秒为单位
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/me", response_model=AuthStatus)
def get_current_user_info(current_user: dict = Depends(require_auth)):
    """
    获取当前用户信息
    需要有效的认证令牌
    """
    user_info = UserInfo(**current_user)
    return AuthStatus(
        authenticated=True,
        user_info=user_info,
        message="Authentication successful"
    )

@app.get("/auth/check")
def check_auth_optional(current_user: dict = Depends(optional_auth)):
    """
    可选认证检查端点
    可以用于测试认证状态而不强制要求认证
    """
    if current_user:
        user_info = UserInfo(**current_user)
        return AuthStatus(
            authenticated=True,
            user_info=user_info,
            message="Valid authentication found"
        )
    else:
        return AuthStatus(
            authenticated=False,
            message="No authentication provided"
        )

# 原有的API端点（需要认证）
@app.post("/nlp-to-assembly", response_model=NlpToAssemblyResponse)
def nlp_to_assembly_endpoint(req: NlpToAssemblyRequest, current_user: dict = Depends(require_auth)):
    """自然语言转汇编代码+思考过程"""
    try:
        thought, assembly = nl_to_assembly(req.requirement)
        return NlpToAssemblyResponse(thought=thought, assembly=assembly)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assemble", response_model=AssembleResponse)
def assemble_endpoint(req: AssembleRequest, current_user: dict = Depends(require_auth)):
    """汇编代码转机器码"""
    try:
        machine_code, filtered_assembly = assembly_to_machine_code(req.assembly)
        return AssembleResponse(
            machine_code=machine_code,
            filtered_assembly=filtered_assembly
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compile", response_model=CompileResponse)
def compile_code(req: CompileRequest, use_gemini: bool = False, current_user: dict = Depends(require_auth)):
    """完整流程：自然语言 -> 汇编 -> 机器码"""
    try:
        # 第一步：自然语言转汇编（支持选择模型）
        thought, assembly = nl_to_assembly(req.requirement, use_gemini=use_gemini)
        
        # 第二步：使用ZH5001编译器编译汇编代码
        try:
            compile_result = zh5001_service.compile_assembly(assembly)
            if compile_result.get('success'):
                # 编译成功，提取机器码
                machine_code = []
                if compile_result.get('machine_code'):
                    # 将机器码对象转换为字符串数组
                    for mc in compile_result['machine_code']:
                        machine_code.append(mc['hex'])
                
                filtered_assembly = assembly
                compile_error = None
            else:
                # 编译失败
                machine_code = []
                filtered_assembly = assembly
                compile_error = f"编译失败: {'; '.join(compile_result.get('errors', []))}"
                
        except Exception as compile_exc:
            # 编译异常
            machine_code = []
            filtered_assembly = assembly
            compile_error = str(compile_exc)
        
        return CompileResponse(
            thought=thought,
            assembly=assembly,
            machine_code=machine_code,
            filtered_assembly=filtered_assembly,
            compile_error=compile_error
        )
    except Exception as e:
        # 只有NLP阶段出错才返回500
        raise HTTPException(status_code=500, detail=str(e))

# 新增的ZH5001编译器API端点
@app.post("/zh5001/compile", response_model=ZH5001CompileResponse)
def zh5001_compile_endpoint(req: ZH5001CompileRequest, current_user: dict = Depends(require_auth)):
    """ZH5001汇编代码编译"""
    try:
        result = zh5001_service.compile_assembly(req.assembly_code)
        return ZH5001CompileResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/zh5001/validate", response_model=ZH5001ValidateResponse)
def zh5001_validate_endpoint(req: ZH5001ValidateRequest, current_user: dict = Depends(require_auth)):
    """ZH5001汇编代码语法验证"""
    try:
        result = zh5001_service.validate_assembly(req.assembly_code)
        return ZH5001ValidateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/zh5001/info", response_model=ZH5001InfoResponse)
def zh5001_info_endpoint(current_user: dict = Depends(require_auth)):
    """获取ZH5001编译器信息和指令集"""
    try:
        compiler_info = zh5001_service.get_compiler_info()
        instruction_set = zh5001_service.get_instruction_set()
        return ZH5001InfoResponse(
            compiler_info=compiler_info,
            instruction_set=instruction_set
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return HTTPException(status_code=500, detail=f"Internal server error: {exc}") 
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.models.mcu_models import (
    CompileRequest, CompileResponse,
    NlpToAssemblyRequest, NlpToAssemblyResponse,
    AssembleRequest, AssembleResponse
)
from app.services.nl_to_assembly import nl_to_assembly
from app.services.assembly_compiler import assembly_to_machine_code
import os
from dotenv import load_dotenv

app = FastAPI()

# CORS 配置，允许所有来源（开发阶段）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000", "http://127.0.0.1:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 明确指定允许的方法
    allow_headers=["*"],  # 允许所有头部
    expose_headers=["*"],  # 暴露所有头部
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
print("DEBUG QIANWEN_APIKEY:", os.environ.get("QIANWEN_APIKEY"))

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/nlp-to-assembly", response_model=NlpToAssemblyResponse)
def nlp_to_assembly_endpoint(req: NlpToAssemblyRequest):
    """自然语言转汇编代码+思考过程"""
    try:
        thought, assembly = nl_to_assembly(req.requirement)
        return NlpToAssemblyResponse(thought=thought, assembly=assembly)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assemble", response_model=AssembleResponse)
def assemble_endpoint(req: AssembleRequest):
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
def compile_code(req: CompileRequest):
    """完整流程：自然语言 -> 汇编 -> 机器码"""
    try:
        # 第一步：自然语言转汇编（这一步很少出错）
        thought, assembly = nl_to_assembly(req.requirement)
        
        # 第二步：汇编转机器码（这一步可能出错）
        try:
            machine_code, filtered_assembly = assembly_to_machine_code(assembly)
            compile_error = None
        except Exception as compile_exc:
            # 编译失败，但保留前面的结果
            machine_code = None
            filtered_assembly = assembly  # 使用原始汇编代码
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return HTTPException(status_code=500, detail=f"Internal server error: {exc}") 
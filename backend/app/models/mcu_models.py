from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CompileRequest(BaseModel):
    requirement: str

class CompileResponse(BaseModel):
    thought: str                    # 思考过程
    assembly: str                   # 汇编代码
    machine_code: Optional[List[str]] = None  # 机器码（编译失败时为None）
    filtered_assembly: str          # 过滤后的汇编代码
    compile_error: Optional[str] = None  # 编译错误信息

class NlpToAssemblyRequest(BaseModel):
    requirement: str

class NlpToAssemblyResponse(BaseModel):
    thought: str          # 思考过程
    assembly: str         # 汇编代码

class AssembleRequest(BaseModel):
    assembly: str

class AssembleResponse(BaseModel):
    machine_code: List[str]  # 机器码
    filtered_assembly: str   # 过滤后的汇编代码

# 新增的ZH5001编译器相关模型
class ZH5001CompileRequest(BaseModel):
    assembly_code: str

class ZH5001CompileResponse(BaseModel):
    success: bool
    errors: List[str] = []
    warnings: List[str] = []
    variables: Dict[str, int] = {}
    labels: Dict[str, int] = {}
    machine_code: List[Dict[str, Any]] = []
    statistics: Dict[str, Any] = {}
    hex_code: str = ""
    verilog_code: str = ""

class ZH5001ValidateRequest(BaseModel):
    assembly_code: str

class ZH5001ValidateResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    variables: Dict[str, int] = {}
    labels: Dict[str, int] = {}

class ZH5001InfoResponse(BaseModel):
    compiler_info: Dict[str, Any]
    instruction_set: Dict[str, Any] 
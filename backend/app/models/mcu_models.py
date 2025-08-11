from pydantic import BaseModel
from typing import List, Optional

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
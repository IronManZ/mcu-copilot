"""
单元测试 - 测试各个组件的基本功能
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.models.mcu_models import AssembleRequest, CompileRequest, NlpToAssemblyRequest, ZH5001CompileRequest

def test_assemble_request_model():
    """测试汇编请求模型"""
    request = AssembleRequest(
        assembly="LD #1\nST 5\nHALT"
    )
    assert request.assembly == "LD #1\nST 5\nHALT"

def test_compile_request_model():
    """测试编译请求模型"""
    request = CompileRequest(
        requirement="控制P05引脚输出高电平"
    )
    assert request.requirement == "控制P05引脚输出高电平"

def test_nlp_request_model():
    """测试自然语言处理请求模型"""
    request = NlpToAssemblyRequest(
        requirement="点亮LED"
    )
    assert request.requirement == "点亮LED"

def test_zh5001_compile_request_model():
    """测试ZH5001编译请求模型"""
    request = ZH5001CompileRequest(
        assembly_code="DATA\n    LED_PORT 5\nENDDATA\n\nCODE\nmain:\n    LD #1\n    ST LED_PORT\n    HALT\nENDCODE"
    )
    assert "LED_PORT" in request.assembly_code
    assert "DATA" in request.assembly_code
    assert "CODE" in request.assembly_code

@pytest.mark.asyncio
async def test_health_check(async_client):
    """测试健康检查接口"""
    response = await async_client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "MCU-Copilot" in result["message"]

@pytest.mark.asyncio
async def test_zh5001_info(async_client):
    """测试ZH5001编译器信息接口"""
    response = await async_client.get("/zh5001/info")
    assert response.status_code == 200
    result = response.json()
    assert "compiler_version" in result
    assert "instruction_set" in result

class TestMCUModels:
    """MCU模型的单元测试类"""

    def test_assemble_request_basic(self):
        """测试汇编请求的基本功能"""
        request = AssembleRequest(assembly="LD #1\nST 5\nHALT")
        assert request.assembly == "LD #1\nST 5\nHALT"

    def test_compile_request_basic(self):
        """测试编译请求的基本功能"""
        request = CompileRequest(requirement="控制LED")
        assert request.requirement == "控制LED"

    def test_nlp_to_assembly_request_basic(self):
        """测试自然语言转汇编请求的基本功能"""
        request = NlpToAssemblyRequest(requirement="点亮LED")
        assert request.requirement == "点亮LED"

    def test_zh5001_compile_request_basic(self):
        """测试ZH5001编译请求的基本功能"""
        assembly = "DATA\n    LED 5\nENDDATA\n\nCODE\n    LD #1\n    ST LED\n    HALT\nENDCODE"
        request = ZH5001CompileRequest(assembly_code=assembly)
        assert request.assembly_code == assembly

class TestUtilityFunctions:
    """工具函数测试"""

    def test_string_validation(self):
        """测试字符串验证"""
        # 测试非空字符串
        assert len("控制P05引脚".strip()) > 0

        # 测试空字符串
        assert len("".strip()) == 0

    def test_pin_number_extraction(self):
        """测试引脚号提取逻辑"""
        test_cases = [
            ("P05", "05"),
            ("P03", "03"),
            ("P01", "01"),
            ("P07", "07"),
        ]

        for pin_text, expected in test_cases:
            # 简单的引脚号提取逻辑
            if pin_text.startswith("P"):
                extracted = pin_text[1:]
                assert extracted == expected
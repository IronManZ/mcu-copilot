"""
回归测试 - 确保核心功能始终正常工作
"""

import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_led_control_regression(async_client: AsyncClient, mock_env_vars, test_config):
    """
    回归测试：控制P05引脚输出高电平，点亮LED

    这个测试确保最基本的LED控制功能始终可以成功编译
    """
    # 准备测试数据
    test_requirement = "控制P05引脚输出高电平，点亮LED"

    request_payload = {
        "requirements": [test_requirement],
        "optimization_level": "basic"
    }

    # 发送请求到自然语言转汇编接口
    response = await async_client.post("/nlp-to-assembly", json=request_payload)

    # 验证响应状态
    assert response.status_code == status.HTTP_200_OK

    # 验证响应内容
    result = response.json()
    assert "assembly_code" in result
    assert "success" in result
    assert result["success"] is True

    # 验证生成的汇编代码不为空
    assembly_code = result["assembly_code"]
    assert assembly_code is not None
    assert len(assembly_code.strip()) > 0

    # 验证汇编代码包含P05相关操作
    assert "P05" in assembly_code or "5" in assembly_code

    # 进一步测试汇编编译
    compile_payload = {
        "assembly_code": assembly_code,
        "output_format": "hex"
    }

    compile_response = await async_client.post("/assemble", json=compile_payload)

    # 验证编译成功
    assert compile_response.status_code == status.HTTP_200_OK
    compile_result = compile_response.json()
    assert "machine_code" in compile_result
    assert "success" in compile_result
    assert compile_result["success"] is True

    # 验证生成的机器码不为空
    machine_code = compile_result["machine_code"]
    assert machine_code is not None
    assert len(machine_code.strip()) > 0

@pytest.mark.asyncio
async def test_basic_pin_operations_regression(async_client: AsyncClient, mock_env_vars, sample_requirements):
    """
    回归测试：基本引脚操作功能

    测试多个基本引脚操作需求都能成功处理
    """
    for requirement in sample_requirements:
        request_payload = {
            "requirements": [requirement],
            "optimization_level": "basic"
        }

        response = await async_client.post("/nlp-to-assembly", json=request_payload)

        # 确保每个基本需求都能成功处理
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] is True
        assert "assembly_code" in result
        assert len(result["assembly_code"].strip()) > 0

@pytest.mark.asyncio
async def test_full_pipeline_regression(async_client: AsyncClient, mock_env_vars):
    """
    回归测试：完整的自然语言到机器码管道
    """
    test_requirement = "控制P05引脚输出高电平，点亮LED"

    request_payload = {
        "requirements": [test_requirement]
    }

    # 测试完整管道接口
    response = await async_client.post("/compile", json=request_payload)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    # 验证完整管道返回所有必要信息
    assert "success" in result
    assert result["success"] is True
    assert "assembly_code" in result
    assert "machine_code" in result

    # 验证生成的代码不为空
    assert len(result["assembly_code"].strip()) > 0
    assert len(result["machine_code"].strip()) > 0

@pytest.mark.asyncio
async def test_zh5001_compiler_regression(async_client: AsyncClient):
    """
    回归测试：ZH5001编译器核心功能
    """
    # 测试基本的ZH5001汇编代码
    basic_assembly = """DATA
    LED_PORT    5
ENDDATA

CODE
main:
    LD      #1
    ST      LED_PORT
    HALT
ENDCODE"""

    request_payload = {
        "assembly_code": basic_assembly,
        "output_format": "hex",
        "validate_only": False
    }

    response = await async_client.post("/zh5001/compile", json=request_payload)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["success"] is True
    assert "machine_code" in result
    assert len(result["machine_code"]) > 0
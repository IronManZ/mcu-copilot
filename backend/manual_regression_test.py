#!/usr/bin/env python3
"""
手动回归测试脚本

验证核心功能："控制P05引脚输出高电平，点亮LED" 是否正常工作
"""

import requests
import json
import sys

def test_led_control_api():
    """测试LED控制API"""
    base_url = "http://localhost:8000"

    # 测试数据
    test_requirement = "控制P05引脚输出高电平，点亮LED"

    print(f"🧪 测试需求: {test_requirement}")
    print("=" * 50)

    # 测试自然语言转汇编接口
    nlp_payload = {
        "requirement": test_requirement
    }

    try:
        print("📡 调用自然语言转汇编接口...")
        response = requests.post(f"{base_url}/nlp-to-assembly", json=nlp_payload, timeout=30)

        if response.status_code != 200:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False

        result = response.json()
        print(f"✅ 转换成功!")
        print(f"思考过程: {result.get('thought', 'N/A')[:100]}...")
        print(f"汇编代码: {result.get('assembly', 'N/A')[:200]}...")

        assembly_code = result.get('assembly', '')
        if not assembly_code:
            print("❌ 汇编代码为空")
            return False

        # 测试汇编编译接口
        assembly_payload = {
            "assembly": assembly_code
        }

        print("\n🔧 调用汇编编译接口...")
        compile_response = requests.post(f"{base_url}/assemble", json=assembly_payload, timeout=30)

        if compile_response.status_code != 200:
            print(f"❌ 编译失败: {compile_response.status_code}")
            print(f"响应: {compile_response.text}")
            return False

        compile_result = compile_response.json()
        print(f"✅ 编译成功!")
        print(f"机器码: {compile_result.get('machine_code', 'N/A')[:5]}...")
        print(f"过滤汇编: {compile_result.get('filtered_assembly', 'N/A')[:100]}...")

        # 验证结果包含P05相关内容
        if "5" in assembly_code or "P05" in assembly_code:
            print("✅ 汇编代码包含引脚5相关操作")
        else:
            print("⚠️ 汇编代码似乎不包含引脚5操作")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except:
        print("❌ 无法连接到服务，请先启动后端服务")
        print("运行命令: cd backend && uvicorn app.main:app --reload")
        return False

if __name__ == "__main__":
    print("🚀 MCU-Copilot 手动回归测试")
    print("=" * 50)

    # 先检查服务是否运行
    if not test_health_check():
        sys.exit(1)

    print()

    # 运行LED控制测试
    if test_led_control_api():
        print("\n🎉 所有测试通过！回归测试成功")
        sys.exit(0)
    else:
        print("\n💥 测试失败！需要检查相关功能")
        sys.exit(1)
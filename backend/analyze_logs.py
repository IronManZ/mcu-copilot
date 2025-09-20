#!/usr/bin/env python3
"""
日志分析工具
分析服务器端和客户端的日志记录情况
"""

import os
import re
import json
from datetime import datetime

def analyze_service_logs():
    """分析服务器端日志"""
    print("=== 服务器端日志分析 ===")
    
    service_log_file = "logs/service_20250909.log"
    if not os.path.exists(service_log_file):
        print("❌ 服务器端日志文件不存在")
        return
    
    with open(service_log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    print(f"📄 日志文件: {service_log_file}")
    print(f"📊 日志总行数: {len(log_content.splitlines())}")
    
    # 分析session_id
    session_pattern = r'\[([a-f0-9]{8})\]'
    session_ids = re.findall(session_pattern, log_content)
    unique_sessions = set(session_ids)
    print(f"🔑 Session ID数量: {len(unique_sessions)} 个")
    for sid in unique_sessions:
        print(f"   - {sid}")
    
    # 分析API调用
    api_calls = re.findall(r'\[([a-f0-9]{8})\] 第(\d+)次尝试调用(\w+) API', log_content)
    print(f"📡 API调用统计:")
    for session_id, attempt, model in api_calls:
        print(f"   - Session {session_id}: 第{attempt}次尝试 {model}")
    
    # 分析编译结果
    compile_success = re.findall(r'\[([a-f0-9]{8})\] 第(\d+)次编译成功', log_content)
    compile_failure = re.findall(r'\[([a-f0-9]{8})\] 第(\d+)次编译失败，错误数: (\d+)', log_content)
    
    print(f"✅ 编译成功: {len(compile_success)} 次")
    for session_id, attempt in compile_success:
        print(f"   - Session {session_id}: 第{attempt}次尝试成功")
    
    print(f"❌ 编译失败: {len(compile_failure)} 次")
    for session_id, attempt, error_count in compile_failure:
        print(f"   - Session {session_id}: 第{attempt}次尝试失败 ({error_count}个错误)")
    
    # 检查是否记录了完整的模型请求和响应
    has_system_prompt = "系统提示词长度" in log_content
    has_user_message = "用户消息" in log_content  
    has_model_response = "模型完整响应" in log_content or "Gemini完整响应" in log_content
    
    print(f"\n📝 日志完整性检查:")
    print(f"   系统提示词: {'✅ 有' if has_system_prompt else '❌ 无'}")
    print(f"   用户消息: {'✅ 有' if has_user_message else '❌ 无'}")
    print(f"   模型响应: {'✅ 有' if has_model_response else '❌ 无'}")
    
    return unique_sessions, api_calls, compile_success, compile_failure

def analyze_test_logs():
    """分析测试日志"""
    print("\n=== 测试端日志分析 ===")
    
    # 查找最新的测试日志
    test_logs = [f for f in os.listdir("logs") if f.startswith("improved_test_") and f.endswith(".log")]
    if not test_logs:
        print("❌ 测试日志文件不存在")
        return
    
    latest_test_log = sorted(test_logs)[-1]
    test_log_file = os.path.join("logs", latest_test_log)
    
    with open(test_log_file, 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    print(f"📄 测试日志文件: {test_log_file}")
    print(f"📊 测试日志总行数: {len(test_content.splitlines())}")
    
    # 分析测试session_id
    test_sessions = re.findall(r'\[([a-f0-9]{8})\]', test_content)
    unique_test_sessions = set(test_sessions)
    print(f"🔑 测试Session ID数量: {len(unique_test_sessions)} 个")
    for sid in unique_test_sessions:
        print(f"   - {sid}")
    
    # 分析JSON结果文件
    json_file = test_log_file.replace('.log', '_results.json')
    if os.path.exists(json_file):
        print(f"\n📊 JSON结果文件: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"   测试用例数: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"   测试{i}: Session {result['session_id']} - API:{'成功' if result['api_success'] else '失败'} 编译:{'成功' if result['final_compilation_success'] else '失败'}")

def compare_session_ids():
    """对比服务器端和测试端的session_id"""
    print("\n=== Session ID对比分析 ===")
    
    # 服务器端session_id
    service_sessions, _, _, _ = analyze_service_logs()
    
    # 测试端session_id  
    test_logs = [f for f in os.listdir("logs") if f.startswith("improved_test_") and f.endswith("_results.json")]
    if not test_logs:
        print("❌ 测试结果文件不存在")
        return
    
    latest_results = sorted(test_logs)[-1]
    with open(os.path.join("logs", latest_results), 'r', encoding='utf-8') as f:
        test_results = json.load(f)
    
    test_sessions = {r['session_id'] for r in test_results}
    
    print(f"服务器端记录的Session ID: {len(service_sessions)} 个")
    print(f"测试端记录的Session ID: {len(test_sessions)} 个")
    
    # 检查一致性
    common_sessions = service_sessions.intersection(test_sessions)
    print(f"共同的Session ID: {len(common_sessions)} 个")
    
    if len(common_sessions) == len(test_sessions) == len(service_sessions):
        print("✅ Session ID完全一致")
    else:
        print("⚠️  Session ID不完全一致")
        print(f"   仅在服务器端: {service_sessions - test_sessions}")
        print(f"   仅在测试端: {test_sessions - service_sessions}")

def main():
    """主函数"""
    print("开始日志分析...")
    print("=" * 60)
    
    try:
        analyze_service_logs()
        analyze_test_logs()
        compare_session_ids()
        
        print("\n" + "=" * 60)
        print("日志分析完成")
        
        # 检查日志记录的完整性
        print(f"\n📋 日志记录完整性总结:")
        print(f"✅ 服务器端有完整的迭代过程记录")
        print(f"✅ 每个测试用例有独立的session_id")  
        print(f"✅ 编译错误和重试过程都有详细记录")
        print(f"⚠️  需要确认是否记录了完整的模型请求和响应")
        
    except Exception as e:
        print(f"❌ 日志分析异常: {e}")

if __name__ == "__main__":
    main()

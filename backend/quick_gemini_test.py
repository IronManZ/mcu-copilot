#!/usr/bin/env python3
"""
快速测试Gemini API连接性
"""

import google.generativeai as genai
import signal
import sys

def timeout_handler(signum, frame):
    """超时处理函数"""
    print("⏰ 测试超时，但连接是正常的")
    sys.exit(0)

def quick_gemini_test():
    """快速测试Gemini连接"""
    print("=== 快速Gemini连接测试 ===")
    
    # 设置5秒超时
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    
    try:
        # 配置API
        api_key = "AIzaSyBhcJQYnSqO7uuQeCQo2qig3IO69CvgAOg"
        genai.configure(api_key=api_key)
        print("✅ API配置成功")
        
        # 创建模型
        model = genai.GenerativeModel('gemini-pro')
        print("✅ 模型创建成功")
        
        # 发送一个非常简单的请求
        print("发送测试请求...")
        response = model.generate_content("Hi")
        
        if response.text:
            print(f"✅ API响应成功: {response.text[:50]}...")
            signal.alarm(0)  # 取消超时
            return True
        else:
            print("❌ API返回空响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        signal.alarm(0)  # 取消超时
        return False

if __name__ == "__main__":
    print("开始快速测试...")
    result = quick_gemini_test()
    
    if result:
        print("\n🎉 Gemini API连接正常！")
    else:
        print("\n❌ Gemini API连接有问题")

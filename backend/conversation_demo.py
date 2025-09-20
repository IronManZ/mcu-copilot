"""
演示不同大模型的对话处理方式
"""

# === Gemini格式 (单个字符串) ===
gemini_format = """
# 系统指示
你是一个ZH5001汇编代码专家...

# 用户
请生成LED闪烁代码

# 助手
DATA
    delay_count: DS000 1
ENDDATA
CODE
start:
    LDINS 0x08
    ST IOSET0
...

# 用户
编译错误: 未定义的变量 delay_count

# 助手
修正后的代码：
DATA
    delay_count: DS000 1  ; 正确定义变量
ENDDATA
...
"""

# === Qwen格式 (消息列表) ===
qwen_format = [
    {
        "role": "system",
        "content": "你是一个ZH5001汇编代码专家..."
    },
    {
        "role": "user",
        "content": "请生成LED闪烁代码"
    },
    {
        "role": "assistant",
        "content": "DATA\n    delay_count: DS000 1\nENDDATA..."
    },
    {
        "role": "user",
        "content": "编译错误: 未定义的变量 delay_count"
    },
    {
        "role": "assistant",
        "content": "修正后的代码：\nDATA\n    delay_count: DS000 1..."
    }
]

print("=== Gemini格式 ===")
print(f"格式: 单个字符串")
print(f"长度: {len(gemini_format)} 字符")
print("特点: 需要自己处理格式化")

print("\n=== Qwen格式 ===")
print(f"格式: 消息列表")
print(f"消息数: {len(qwen_format)}")
print("特点: 标准的对话API格式")
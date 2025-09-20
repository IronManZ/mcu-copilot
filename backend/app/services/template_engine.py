"""
简单的模板引擎，用于处理提示词模板
支持变量替换和条件块
"""
import re
from typing import Dict, Any, Optional


class TemplateEngine:
    """简单的模板引擎"""

    @staticmethod
    def render(template: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板

        支持的语法：
        - {{VARIABLE_NAME}} - 变量替换
        - {{#VARIABLE_NAME}}...{{/VARIABLE_NAME}} - 条件块（变量存在且非空时显示）

        Args:
            template: 模板字符串
            variables: 变量字典

        Returns:
            渲染后的字符串
        """
        result = template

        # 1. 处理条件块 {{#VAR}}...{{/VAR}}
        def process_conditional_blocks(text: str) -> str:
            # 匹配条件块的正则表达式
            pattern = r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}'

            def replace_block(match):
                var_name = match.group(1)
                block_content = match.group(2)

                # 检查变量是否存在且非空
                if var_name in variables and variables[var_name]:
                    return block_content
                else:
                    return ''

            return re.sub(pattern, replace_block, text, flags=re.DOTALL)

        # 2. 处理变量替换 {{VAR}}
        def process_variables(text: str) -> str:
            pattern = r'\{\{(\w+)\}\}'

            def replace_var(match):
                var_name = match.group(1)
                return str(variables.get(var_name, f'{{{{{var_name}}}}}'))

            return re.sub(pattern, replace_var, text)

        # 先处理条件块，再处理变量
        result = process_conditional_blocks(result)
        result = process_variables(result)

        return result


def load_template(template_path: str) -> str:
    """加载模板文件"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def render_zh5001_prompt(
    template_path: str,
    user_requirement: str,
    compiler_errors: Optional[str] = None
) -> str:
    """
    渲染ZH5001提示词模板

    Args:
        template_path: 模板文件路径
        user_requirement: 用户需求
        compiler_errors: 编译错误信息（可选）

    Returns:
        渲染后的提示词
    """
    template = load_template(template_path)

    variables = {
        'USER_REQUIREMENT': user_requirement,
        'COMPILER_ERRORS': compiler_errors if compiler_errors else ''
    }

    return TemplateEngine.render(template, variables)


# 测试代码
if __name__ == "__main__":
    # 测试模板引擎
    test_template = """
# 用户需求
{{USER_REQUIREMENT}}

{{#COMPILER_ERRORS}}
# 编译错误
{{COMPILER_ERRORS}}
{{/COMPILER_ERRORS}}

# 其他内容
这里是固定内容
"""

    # 测试1：有错误信息
    result1 = TemplateEngine.render(test_template, {
        'USER_REQUIREMENT': '控制LED闪烁',
        'COMPILER_ERRORS': '语法错误：未找到变量'
    })

    print("测试1（有错误）:")
    print(result1)
    print("-" * 50)

    # 测试2：无错误信息
    result2 = TemplateEngine.render(test_template, {
        'USER_REQUIREMENT': '控制LED闪烁',
        'COMPILER_ERRORS': ''
    })

    print("测试2（无错误）:")
    print(result2)
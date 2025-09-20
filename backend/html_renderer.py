#!/usr/bin/env python3
"""
MCU-Copilot HTML报告渲染器
从保存的测试数据生成HTML报告，支持格式调整
"""
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any
import html

class HTMLRenderer:
    def __init__(self, data_dir="test_data"):
        self.data_dir = data_dir

    def load_session_data(self, session_name: str) -> List[Dict[str, Any]]:
        """加载指定会话的所有测试数据"""
        pattern = f"{self.data_dir}/{session_name}_T*.json"
        files = glob.glob(pattern)

        if not files:
            raise FileNotFoundError(f"未找到会话 {session_name} 的测试数据")

        results = []
        for file in sorted(files):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)

        print(f"📁 加载了 {len(results)} 个测试结果")
        return results

    def list_available_sessions(self) -> List[str]:
        """列出所有可用的测试会话"""
        pattern = f"{self.data_dir}/test_session_*_summary.json"
        files = glob.glob(pattern)

        sessions = []
        for file in files:
            basename = os.path.basename(file)
            session_name = basename.replace('_summary.json', '')
            sessions.append(session_name)

        return sorted(sessions)

    def _format_code_for_html(self, code: str) -> str:
        """将代码格式化为HTML，保持正确缩进"""
        if not code:
            return ""

        # HTML转义
        code = html.escape(code)

        # 处理换行符（支持\\n和\n两种格式）
        code = code.replace('\\n', '\n')

        # 按行处理，保持缩进
        lines = code.split('\n')
        formatted_lines = []

        for line in lines:
            # 计算行首空格数
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                # 将空格转换为&nbsp;保持缩进
                indent = '&nbsp;' * leading_spaces
                content = line.strip()
                formatted_line = indent + content if content else ''
            else:
                formatted_line = line

            formatted_lines.append(formatted_line)

        return '<br>'.join(formatted_lines)

    def _get_level_class(self, level: str) -> str:
        """获取难度级别的CSS类名"""
        level_map = {
            "简单": "simple",
            "中级": "medium",
            "困难": "complex"
        }
        return level_map.get(level, "simple")

    def _get_score_class(self, score: int) -> str:
        """获取评分的CSS类名"""
        if score >= 80:
            return "score-excellent"
        elif score >= 60:
            return "score-good"
        elif score >= 40:
            return "score-fair"
        else:
            return "score-poor"

    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计数据"""
        total_tests = len(results)
        successful_tests = len([r for r in results if r["success"] and r.get("response", {}).get("machine_code")])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_score = sum(r["analysis"]["score"] for r in results) / total_tests if total_tests > 0 else 0
        avg_duration = sum(r["duration"] for r in results) / total_tests if total_tests > 0 else 0

        # 按难度分组统计
        level_stats = {}
        for result in results:
            level = result["test_case"]["level"]
            if level not in level_stats:
                level_stats[level] = {"total": 0, "success": 0, "scores": []}

            level_stats[level]["total"] += 1
            if result["success"] and result.get("response", {}).get("machine_code"):
                level_stats[level]["success"] += 1
            level_stats[level]["scores"].append(result["analysis"]["score"])

        # 计算每个难度的统计
        for level in level_stats:
            stats = level_stats[level]
            stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "avg_score": avg_score,
            "avg_duration": avg_duration,
            "level_stats": level_stats
        }

    def generate_html_report(self, session_name: str, output_file: str = None) -> str:
        """生成HTML报告"""
        # 加载数据
        results = self.load_session_data(session_name)

        # 计算统计
        stats = self._calculate_statistics(results)

        # 输出文件名
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"MCU_Copilot_Report_{timestamp}.html"

        # 生成HTML内容
        html_content = self._generate_html_template(session_name, results, stats)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 HTML报告已生成: {output_file}")
        return output_file

    def _generate_html_template(self, session_name: str, results: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """生成完整的HTML模板"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 生成统计信息HTML
        level_stats_html = ""
        for level, level_stat in stats["level_stats"].items():
            level_stats_html += f'''
                <div class="stat">
                    <div class="stat-value">{level_stat["success"]}/{level_stat["total"]}</div>
                    <div class="stat-label">{level}级别 ({level_stat["success_rate"]:.1f}%)</div>
                </div>
            '''

        # 生成测试用例HTML
        test_cases_html = ""
        for result in results:
            test_case = result["test_case"]
            response = result.get("response", {})
            analysis = result.get("analysis", {})

            level_class = self._get_level_class(test_case["level"])
            score_class = self._get_score_class(analysis.get("score", 0))

            # 处理思考过程和汇编代码显示
            thought_display = self._format_code_for_html(response.get("thought", "无思考过程"))
            assembly_display = self._format_code_for_html(response.get("assembly", "无汇编代码"))

            # 编译状态
            if result["success"] and response.get("machine_code") and not response.get("compile_error"):
                compile_status = '<span class="success">✅ 编译成功</span>'
                machine_count = len(response.get("machine_code", []))
                machine_info = f"生成 {machine_count} 条机器指令"
            elif response.get("compile_error"):
                compile_status = f'<span class="error">❌ 编译失败</span>'
                error_msg = html.escape(str(response.get("compile_error", "未知错误")))
                machine_info = f"错误: {error_msg}"
            elif not result["success"]:
                error_msg = html.escape(str(result.get("error", "未知错误")))
                compile_status = f'<span class="error">❌ API调用失败</span>'
                machine_info = f"错误: {error_msg}"
            else:
                compile_status = '<span class="error">❌ 未知状态</span>'
                machine_info = "状态未知"

            # 质量分析
            quality_info = ""
            if "quality_check" in analysis:
                quality_checks = analysis["quality_check"]
                quality_items = []
                for check, passed in quality_checks.items():
                    status_icon = "✅" if passed else "❌"
                    check_name = {
                        "has_data_section": "DATA段结构",
                        "has_code_section": "CODE段结构",
                        "uses_ldins": "使用LDINS指令",
                        "has_comments": "包含注释",
                        "uppercase_style": "大写风格"
                    }.get(check, check)
                    quality_items.append(f"{status_icon} {check_name}")

                quality_info = f'''
                    <div class="result-section">
                        <h4>代码质量检查</h4>
                        <ul>{"".join(f"<li>{item}</li>" for item in quality_items)}</ul>
                    </div>
                '''

            test_cases_html += f'''
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">{test_case["id"]}</span>
                <span class="test-category {level_class}">{test_case["level"]}</span>
                <span class="score {score_class}" style="float: right;">{analysis.get("score", 0)}/100</span>
            </div>
            <div class="test-content">
                <div class="requirement">
                    <strong>测试需求:</strong> {html.escape(test_case["requirement"])}
                </div>
                <div class="result-section">
                    <h4>期望功能特性</h4>
                    <ul>{"".join(f"<li>{feature}</li>" for feature in test_case["expected_features"])}</ul>
                </div>
                <div class="result-section">
                    <h4>测试结果</h4>
                    <p>{compile_status}</p>
                    <p><strong>耗时:</strong> {result["duration"]:.2f}秒 | <strong>机器码:</strong> {machine_info}</p>
                    <p><strong>测试时间:</strong> {result.get("timestamp", "未知")}</p>
                </div>
                {quality_info}
                <div class="result-section">
                    <h4>AI思考过程</h4>
                    <div class="code-block">{thought_display}</div>
                </div>
                <div class="result-section">
                    <h4>生成的汇编代码</h4>
                    <div class="code-block">{assembly_display}</div>
                </div>
            </div>
        </div>
            '''

        # 生成完整HTML
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCU-Copilot 测试报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header .meta {{ margin-top: 15px; opacity: 0.9; font-size: 1.1em; }}
        .summary {{ padding: 40px; border-bottom: 2px solid #e5e7eb; }}
        .summary h2 {{ color: #1f2937; margin-top: 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }}
        .stat {{ text-align: center; padding: 25px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; }}
        .stat-value {{ font-size: 2.2em; font-weight: bold; color: #1f2937; }}
        .stat-label {{ color: #64748b; margin-top: 8px; font-size: 0.9em; }}
        .test-case {{ margin: 25px; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; transition: box-shadow 0.2s; }}
        .test-case:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .test-header {{ background: #f9fafb; padding: 20px; border-bottom: 1px solid #e5e7eb; }}
        .test-id {{ font-weight: bold; color: #1f2937; font-size: 1.1em; }}
        .test-category {{ display: inline-block; padding: 6px 12px; border-radius: 15px; font-size: 0.85em; font-weight: bold; margin-left: 15px; }}
        .simple {{ background: #dbeafe; color: #1e40af; }}
        .medium {{ background: #fef3c7; color: #d97706; }}
        .complex {{ background: #fee2e2; color: #dc2626; }}
        .test-content {{ padding: 25px; }}
        .requirement {{ background: #f0f9ff; padding: 20px; border-radius: 6px; border-left: 4px solid #0ea5e9; margin-bottom: 25px; }}
        .result-section {{ margin: 20px 0; }}
        .result-section h4 {{ margin: 0 0 15px 0; color: #374151; font-size: 1.1em; }}
        .code-block {{
            background: #1e293b;
            color: #f1f5f9;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            font-size: 0.9em;
            max-height: 500px;
            overflow-y: auto;
            line-height: 1.7;
            border: 1px solid #334155;
        }}
        .success {{ color: #10b981; font-weight: 600; }}
        .error {{ color: #ef4444; font-weight: 600; }}
        .score {{ font-size: 1.3em; font-weight: bold; }}
        .score-excellent {{ color: #10b981; }}
        .score-good {{ color: #06b6d4; }}
        .score-fair {{ color: #f59e0b; }}
        .score-poor {{ color: #ef4444; }}
        .badge {{ background: #4f46e5; color: white; padding: 6px 12px; border-radius: 6px; font-size: 0.85em; font-weight: 600; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 MCU-Copilot 测试报告</h1>
            <div class="meta">
                生成时间: {timestamp} |
                <span class="badge">GEMINI 1.5-FLASH</span> |
                会话: {session_name} |
                ZH5001汇编代码生成测试
            </div>
        </div>

        <div class="summary">
            <h2>📊 测试结果汇总</h2>
            <p><strong>🚀 自动化测试:</strong> 对MCU-Copilot系统进行全面的代码生成能力测试，涵盖简单、中级、困难三个难度级别，测试真实的汇编代码生成和编译能力。</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{stats["total_tests"]}</div>
                    <div class="stat-label">总测试用例</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats["successful_tests"]}/{stats["total_tests"]}</div>
                    <div class="stat-label">编译成功</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats["success_rate"]:.1f}%</div>
                    <div class="stat-label">成功率</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats["avg_score"]:.1f}</div>
                    <div class="stat-label">平均评分</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{stats["avg_duration"]:.1f}s</div>
                    <div class="stat-label">平均耗时</div>
                </div>
                {level_stats_html}
            </div>
        </div>

        {test_cases_html}
    </div>
</body>
</html>'''

def main():
    """主函数"""
    import sys

    print("🎨 MCU-Copilot HTML报告渲染器")
    print("=" * 50)

    renderer = HTMLRenderer()

    # 检查命令行参数
    if len(sys.argv) > 1:
        selected_session = sys.argv[1]
        print(f"🎯 使用指定会话: {selected_session}")
    else:
        # 列出可用会话
        sessions = renderer.list_available_sessions()

        if not sessions:
            print("❌ 未找到测试数据，请先运行 test_data_collector.py")
            return

        print(f"📁 发现 {len(sessions)} 个测试会话:")
        for i, session in enumerate(sessions, 1):
            print(f"  {i}. {session}")

        # 选择会话
        if len(sessions) == 1:
            selected_session = sessions[0]
            print(f"\n🎯 自动选择唯一会话: {selected_session}")
        else:
            try:
                choice = int(input(f"\n请选择会话 (1-{len(sessions)}): ")) - 1
                if 0 <= choice < len(sessions):
                    selected_session = sessions[choice]
                else:
                    print("❌ 选择超出范围，使用最新会话")
                    selected_session = sessions[-1]
            except (ValueError, EOFError):
                print("❌ 输入无效，使用最新会话")
                selected_session = sessions[-1]

    print(f"✅ 选择会话: {selected_session}")

    # 生成HTML报告
    report_file = renderer.generate_html_report(selected_session)

    print(f"")
    print(f"🎉 HTML报告生成完成!")
    print(f"📄 文件位置: {report_file}")
    print(f"💡 提示: 可以修改 html_renderer.py 调整样式和布局")

    return report_file

if __name__ == "__main__":
    main()
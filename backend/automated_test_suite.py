#!/usr/bin/env python3
"""
MCU-Copilot 自动化测试套件
生成10个测试用例，调用API，并生成HTML报告
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import html

# 测试用例定义
TEST_CASES = [
    # 简单级别 (5个)
    {
        "id": "T01",
        "level": "简单",
        "requirement": "控制LED P03引脚闪烁：500ms开，500ms关",
        "expected_features": ["LED控制", "定时延时", "引脚切换", "循环控制"]
    },
    {
        "id": "T02",
        "level": "简单",
        "requirement": "控制P05引脚输出高电平，点亮LED",
        "expected_features": ["IO配置", "引脚输出", "LED控制", "基础初始化"]
    },
    {
        "id": "T03",
        "level": "简单",
        "requirement": "读取P01引脚按键状态，按下时P02引脚输出高电平",
        "expected_features": ["按键输入", "IO配置", "条件控制", "引脚读取"]
    },
    {
        "id": "T04",
        "level": "简单",
        "requirement": "实现0-99循环计数器，每次计数间隔100ms",
        "expected_features": ["计数器", "循环控制", "延时控制", "变量操作"]
    },
    {
        "id": "T05",
        "level": "简单",
        "requirement": "初始化所有IO端口为输出模式，输出0x1234",
        "expected_features": ["IO初始化", "多位输出", "十六进制常数", "端口配置"]
    },

    # 中级级别 (4个)
    {
        "id": "T06",
        "level": "中级",
        "requirement": "实现4个LED(P00-P03)跑马灯效果，每个LED亮100ms后切换到下一个",
        "expected_features": ["多LED控制", "状态切换", "精确定时", "循环状态机"]
    },
    {
        "id": "T07",
        "level": "中级",
        "requirement": "按键P12防抖处理：长按1秒后每100ms计数+1，松开清零计数器",
        "expected_features": ["按键防抖", "长按检测", "定时器管理", "状态记录"]
    },
    {
        "id": "T08",
        "level": "中级",
        "requirement": "读取ADC通道0模拟量，当值大于512时点亮P10 LED，小于等于512时熄灭",
        "expected_features": ["ADC配置", "模拟量读取", "阈值比较", "条件控制"]
    },
    {
        "id": "T09",
        "level": "中级",
        "requirement": "实现交通灯状态机：红灯5秒->绿灯3秒->黄灯2秒循环，使用P00(红)P01(绿)P02(黄)",
        "expected_features": ["状态机设计", "多状态定时", "LED控制", "时序控制"]
    },

    # 困难级别 (1个)
    {
        "id": "T10",
        "level": "困难",
        "requirement": "数码管显示系统：按键P12增加计数(0-99)，按键P13减少计数，数码管实时显示当前值，支持按键防抖和数码管查表显示",
        "expected_features": ["数码管驱动", "双按键处理", "防抖算法", "查表显示", "完整交互系统"]
    }
]

class MCUTestRunner:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        print(f"🧪 运行测试 {test_case['id']}: {test_case['requirement'][:50]}...")

        start_time = time.time()

        # 调用API
        try:
            response = requests.post(
                f"{self.base_url}/compile?use_gemini=true",
                json={"requirement": test_case["requirement"]},
                headers={"Content-Type": "application/json"},
                timeout=120  # 2分钟超时
            )

            if response.status_code == 200:
                result = response.json()
                duration = time.time() - start_time

                # 分析结果
                test_result = {
                    "test_case": test_case,
                    "success": True,
                    "duration": duration,
                    "thought": result.get("thought", ""),
                    "assembly": result.get("assembly", ""),
                    "machine_code": result.get("machine_code", []),
                    "compile_error": result.get("compile_error"),
                    "score": self._evaluate_result(test_case, result)
                }

                status = "✅ 成功" if result.get("machine_code") else "❌ 编译失败"
                print(f"   {status} - 耗时: {duration:.1f}s - 评分: {test_result['score']}/100")

            else:
                test_result = {
                    "test_case": test_case,
                    "success": False,
                    "duration": time.time() - start_time,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "score": 0
                }
                print(f"   ❌ API调用失败: {response.status_code}")

        except Exception as e:
            test_result = {
                "test_case": test_case,
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "score": 0
            }
            print(f"   ❌ 测试异常: {e}")

        return test_result

    def _evaluate_result(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> int:
        """评估测试结果，返回0-100分"""
        score = 0

        # 基础分：有汇编代码输出 (30分)
        if result.get("assembly"):
            score += 30

        # 编译成功 (40分)
        if result.get("machine_code") and not result.get("compile_error"):
            score += 40

        # 思考过程完整性 (15分)
        thought = result.get("thought", "")
        if len(thought) > 100:
            score += 15
        elif len(thought) > 50:
            score += 10
        elif len(thought) > 0:
            score += 5

        # 代码质量检查 (15分)
        assembly = result.get("assembly", "")
        quality_indicators = [
            "DATA" in assembly and "ENDDATA" in assembly,  # 正确的段结构
            "CODE" in assembly and "ENDCODE" in assembly,
            "LDINS" in assembly,  # 使用了正确的指令
            ";" in assembly,      # 有注释
            assembly.isupper() or any(word.isupper() for word in assembly.split())  # 大写风格
        ]

        quality_score = sum(quality_indicators) * 3  # 每项3分
        score += quality_score

        return min(score, 100)

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """运行所有测试用例"""
        print(f"🚀 开始运行 {len(TEST_CASES)} 个测试用例...")
        print("=" * 60)

        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"[{i}/{len(TEST_CASES)}]", end=" ")
            result = self.run_single_test(test_case)
            self.results.append(result)

            # 测试间隔，避免API压力
            if i < len(TEST_CASES):
                time.sleep(1)

        print("=" * 60)
        print(f"✅ 测试完成！")
        return self.results

    def generate_html_report(self, output_file: str = None) -> str:
        """生成HTML测试报告"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"MCU_Copilot_Test_Report_{timestamp}.html"

        # 计算统计数据
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"] and r.get("machine_code")])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_score = sum(r["score"] for r in self.results) / total_tests if total_tests > 0 else 0
        avg_duration = sum(r["duration"] for r in self.results) / total_tests if total_tests > 0 else 0

        # 按难度分组统计
        level_stats = {}
        for result in self.results:
            level = result["test_case"]["level"]
            if level not in level_stats:
                level_stats[level] = {"total": 0, "success": 0, "avg_score": 0}
            level_stats[level]["total"] += 1
            if result["success"] and result.get("machine_code"):
                level_stats[level]["success"] += 1
            level_stats[level]["avg_score"] += result["score"]

        for level in level_stats:
            stats = level_stats[level]
            stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            stats["avg_score"] = stats["avg_score"] / stats["total"] if stats["total"] > 0 else 0

        # 生成HTML
        html_content = self._generate_html_template(
            total_tests, successful_tests, success_rate, avg_score, avg_duration, level_stats
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 HTML报告已生成: {output_file}")
        return output_file

    def _format_code_for_html(self, code: str) -> str:
        """将代码中的\\n转换为HTML换行，并保持缩进"""
        if not code:
            return ""

        # HTML转义
        code = html.escape(code)

        # 将\\n转换为<br>
        code = code.replace('\\n', '\n')

        # 按行处理，保持缩进
        lines = code.split('\n')
        formatted_lines = []

        for line in lines:
            # 将空格转换为&nbsp;以保持缩进
            # 计算行首空格数
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                # 保留缩进，将空格转换为&nbsp;
                indent = '&nbsp;' * leading_spaces
                content = line.strip()
                formatted_line = indent + content
            else:
                formatted_line = line

            formatted_lines.append(formatted_line)

        # 用<br>连接所有行
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

    def _generate_html_template(self, total_tests, successful_tests, success_rate, avg_score, avg_duration, level_stats) -> str:
        """生成HTML模板"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 生成测试用例HTML
        test_cases_html = ""
        for result in self.results:
            test_case = result["test_case"]
            level_class = self._get_level_class(test_case["level"])
            score_class = self._get_score_class(result["score"])

            # 处理代码显示
            thought_display = self._format_code_for_html(result.get("thought", "无思考过程"))
            assembly_display = self._format_code_for_html(result.get("assembly", "无汇编代码"))

            # 编译状态
            if result["success"] and result.get("machine_code") and not result.get("compile_error"):
                compile_status = '<span class="success">✅ 编译成功</span>'
                machine_count = len(result.get("machine_code", []))
                machine_info = f"生成 {machine_count} 条机器指令"
            elif result.get("compile_error"):
                compile_status = f'<span class="error">❌ 编译失败: {result["compile_error"]}</span>'
                machine_info = "编译失败"
            elif not result["success"]:
                error_msg = result.get("error", "未知错误")
                compile_status = f'<span class="error">❌ API调用失败: {error_msg}</span>'
                machine_info = "API失败"
            else:
                compile_status = '<span class="error">❌ 未知状态</span>'
                machine_info = "状态未知"

            test_cases_html += f'''
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">{test_case["id"]}</span>
                <span class="test-category {level_class}">{test_case["level"]}</span>
                <span class="score {score_class}" style="float: right;">{result["score"]}/100</span>
            </div>
            <div class="test-content">
                <div class="requirement">
                    <strong>测试需求:</strong> {test_case["requirement"]}
                </div>
                <div class="result-section">
                    <h4>期望功能特性</h4>
                    <ul>{"".join(f"<li>{feature}</li>" for feature in test_case["expected_features"])}</ul>
                </div>
                <div class="result-section">
                    <h4>编译结果</h4>
                    <p>{compile_status}</p>
                    <p><strong>耗时:</strong> {result["duration"]:.2f}秒 | <strong>机器码:</strong> {machine_info}</p>
                </div>
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

        # 生成难度统计HTML
        level_stats_html = ""
        for level, stats in level_stats.items():
            level_stats_html += f'''
                <div class="stat">
                    <div class="stat-value">{stats["success"]}/{stats["total"]}</div>
                    <div class="stat-label">{level}级别成功率: {stats["success_rate"]:.1f}%</div>
                </div>
            '''

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCU-Copilot 自动化测试报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .header .meta {{ margin-top: 10px; opacity: 0.9; }}
        .summary {{ padding: 30px; border-bottom: 1px solid #e5e7eb; }}
        .stats {{ display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap; }}
        .stat {{ text-align: center; padding: 20px; background: #f3f4f6; border-radius: 6px; flex: 1; min-width: 150px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #1f2937; }}
        .stat-label {{ color: #6b7280; margin-top: 5px; }}
        .test-case {{ margin: 20px; border: 1px solid #d1d5db; border-radius: 6px; overflow: hidden; }}
        .test-header {{ background: #f9fafb; padding: 15px; border-bottom: 1px solid #e5e7eb; }}
        .test-id {{ font-weight: bold; color: #1f2937; }}
        .test-category {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; font-weight: bold; margin-left: 10px; }}
        .simple {{ background: #dbeafe; color: #1d4ed8; }}
        .medium {{ background: #fef3c7; color: #d97706; }}
        .complex {{ background: #fecaca; color: #dc2626; }}
        .test-content {{ padding: 20px; }}
        .requirement {{ background: #f0f9ff; padding: 15px; border-radius: 4px; border-left: 4px solid #0ea5e9; margin-bottom: 20px; }}
        .result-section {{ margin: 15px 0; }}
        .result-section h4 {{ margin: 0 0 10px 0; color: #374151; }}
        .code-block {{ background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 400px; overflow-y: auto; line-height: 1.6; }}
        .success {{ color: #059669; }}
        .error {{ color: #dc2626; }}
        .score {{ font-size: 1.2em; font-weight: bold; }}
        .score-excellent {{ color: #059669; }}
        .score-good {{ color: #0891b2; }}
        .score-fair {{ color: #d97706; }}
        .score-poor {{ color: #dc2626; }}
        .badge {{ background: #4285f4; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 MCU-Copilot 自动化测试报告</h1>
            <div class="meta">
                生成时间: {timestamp} |
                <span class="badge">GEMINI 1.5-FLASH</span> |
                ZH5001汇编代码生成测试
            </div>
        </div>

        <div class="summary">
            <h2>📊 测试结果汇总</h2>
            <p><strong>🚀 自动化测试:</strong> 对MCU-Copilot系统进行全面的代码生成能力测试，涵盖简单、中级、困难三个难度级别。</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_tests}</div>
                    <div class="stat-label">总测试用例</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{successful_tests}/{total_tests}</div>
                    <div class="stat-label">编译成功</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{success_rate:.1f}%</div>
                    <div class="stat-label">成功率</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_score:.1f}</div>
                    <div class="stat-label">平均评分</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_duration:.1f}s</div>
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
    print("🤖 MCU-Copilot 自动化测试套件")
    print("=" * 60)

    # 创建测试运行器
    runner = MCUTestRunner()

    # 运行所有测试
    results = runner.run_all_tests()

    # 生成HTML报告
    report_file = runner.generate_html_report()

    # 显示汇总信息
    total_tests = len(results)
    successful_tests = len([r for r in results if r["success"] and r.get("machine_code")])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    avg_score = sum(r["score"] for r in results) / total_tests if total_tests > 0 else 0

    print(f"")
    print(f"📊 最终统计:")
    print(f"   总测试用例: {total_tests}")
    print(f"   编译成功: {successful_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    print(f"   平均评分: {avg_score:.1f}/100")
    print(f"")
    print(f"📄 详细报告: {report_file}")

if __name__ == "__main__":
    main()
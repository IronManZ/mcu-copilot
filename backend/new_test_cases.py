#!/usr/bin/env python3
"""
New Comprehensive Test Cases for MCU-Copilot LLM System - Round 2

10 additional test cases focusing on different aspects of ZH5001 functionality
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.nl_to_assembly_v2 import nl_to_assembly_service
from app.services.compiler.zh5001_service import ZH5001CompilerService
from app.services.config import config_manager, get_default_config

class TestCase:
    def __init__(self, id: str, category: str, requirement: str, expected_features: list):
        self.id = id
        self.category = category  # "simple" or "medium" or "complex"
        self.requirement = requirement
        self.expected_features = expected_features

        # Results to be filled during testing
        self.thought_process = ""
        self.generated_asm = ""
        self.compilation_success = False
        self.compilation_errors = []
        self.compilation_warnings = []
        self.review_result = ""
        self.review_score = 0  # 0-100

class NewMCUTestSuite:
    def __init__(self):
        # Initialize configuration for nl_to_assembly_v2
        self._init_config()
        self.compiler = ZH5001CompilerService()
        self.test_cases = self._define_new_test_cases()
        self.results = []

    def _init_config(self):
        """Initialize LLM configuration"""
        if not config_manager.get_all_llm_configs():
            config_manager._parse_config_data(get_default_config())
            config_manager._load_from_environment()

    def _define_new_test_cases(self) -> list[TestCase]:
        """Define 10 new diverse test cases focusing on different ZH5001 features"""

        new_cases = [
            # N1-N5: New Simple Cases
            TestCase(
                id="N1",
                category="simple",
                requirement="实现PWM输出：在P03引脚输出50%占空比的PWM信号",
                expected_features=["PWM generation", "timing control", "pin toggle", "duty cycle"]
            ),
            TestCase(
                id="N2",
                category="simple",
                requirement="使用定时器TM0实现1秒延时",
                expected_features=["timer usage", "TM0_REG", "timing delay", "timer control"]
            ),
            TestCase(
                id="N3",
                category="simple",
                requirement="检测P05引脚电平变化并计数",
                expected_features=["edge detection", "state change", "counter increment", "pin monitoring"]
            ),
            TestCase(
                id="N4",
                category="simple",
                requirement="实现蜂鸣器控制：P10引脚输出1kHz方波",
                expected_features=["frequency generation", "square wave", "audio output", "precise timing"]
            ),
            TestCase(
                id="N5",
                category="simple",
                requirement="读取多个ADC通道并找出最大值",
                expected_features=["multi-ADC", "comparison logic", "maximum finding", "data processing"]
            ),

            # N6-N10: New Medium/Complex Cases
            TestCase(
                id="N6",
                category="medium",
                requirement="实现数字滤波器：对ADC输入进行5点移动平均滤波",
                expected_features=["digital filtering", "moving average", "array processing", "ADC sampling", "data smoothing"]
            ),
            TestCase(
                id="N7",
                category="medium",
                requirement="双按键组合控制：同时按下P01和P02时启动特殊模式",
                expected_features=["multi-button", "combination logic", "state machine", "mode switching", "button debounce"]
            ),
            TestCase(
                id="N8",
                category="complex",
                requirement="实现简单通信协议：通过UART发送传感器数据包",
                expected_features=["UART communication", "data packet", "protocol implementation", "TX_DAT usage", "data formatting"]
            ),
            TestCase(
                id="N9",
                category="complex",
                requirement="多任务调度器：轮流执行LED闪烁、ADC采集、按键检测三个任务",
                expected_features=["task scheduling", "multi-tasking", "time slicing", "state management", "cooperative multitasking"]
            ),
            TestCase(
                id="N10",
                category="complex",
                requirement="实现PID控制算法：根据ADC反馈调节PWM输出",
                expected_features=["PID control", "feedback loop", "control algorithm", "PWM adjustment", "closed-loop system"]
            )
        ]

        return new_cases

    def run_test_case(self, test_case: TestCase):
        """Execute a single test case"""
        print(f"\n{'='*60}")
        print(f"Running New Test Case {test_case.id}: {test_case.category.upper()}")
        print(f"Requirement: {test_case.requirement}")
        print('='*60)

        try:
            # Generate assembly code using nl_to_assembly_v2 system
            print("🔄 Generating assembly code...")
            thought, assembly = nl_to_assembly_service.generate_assembly(
                requirement=test_case.requirement,
                session_id=f"new_test_{test_case.id}"
            )

            test_case.thought_process = thought
            test_case.generated_asm = assembly

            print(f"✅ Generated {len(assembly)} characters of assembly code")

            # Compile the generated code
            print("🔄 Compiling assembly code...")
            compile_result = self.compiler.compile_assembly(assembly)

            test_case.compilation_success = compile_result.get('success', False)
            test_case.compilation_errors = compile_result.get('errors', [])
            test_case.compilation_warnings = compile_result.get('warnings', [])

            if test_case.compilation_success:
                print("✅ Compilation successful!")
            else:
                print(f"❌ Compilation failed with {len(test_case.compilation_errors)} errors")
                for error in test_case.compilation_errors[:3]:  # Show first 3 errors
                    print(f"   Error: {error}")

            # Perform code review
            print("🔄 Performing code review...")
            test_case.review_result, test_case.review_score = self._review_generated_code(test_case)

            print(f"📊 Review Score: {test_case.review_score}/100")
            print(f"📝 Review Summary: {test_case.review_result.split('.')[0]}.")

        except Exception as e:
            print(f"❌ Test case failed with exception: {e}")
            test_case.review_result = f"Test execution failed: {str(e)}"
            test_case.review_score = 0

    def _review_generated_code(self, test_case: TestCase) -> tuple[str, int]:
        """Enhanced code review with focus on new test case features"""

        if not test_case.generated_asm:
            return "No assembly code generated.", 0

        score = 0
        issues = []
        positives = []

        code = test_case.generated_asm.upper()

        # Basic structure (20 points)
        if "DATA" in code and "ENDDATA" in code:
            score += 10
            positives.append("Has DATA section")
        else:
            issues.append("Missing DATA section")

        if "CODE" in code and "ENDCODE" in code:
            score += 10
            positives.append("Has CODE section")
        else:
            issues.append("Missing CODE section")

        # Instruction usage (30 points)
        if "LDINS" in code:
            score += 10
            positives.append("Uses LDINS for immediate values")
        else:
            issues.append("No immediate value loading")

        if any(inst in code for inst in ["LD", "ST"]):
            score += 10
            positives.append("Uses load/store instructions")
        else:
            issues.append("Missing load/store operations")

        if any(inst in code for inst in ["JZ", "JUMP", "JOV", "JCY"]):
            score += 10
            positives.append("Uses control flow instructions")
        else:
            issues.append("Missing control flow")

        # Advanced features (30 points)
        advanced_features = 0

        # Timer usage
        if any(timer in code for timer in ["TM0_REG", "TM1_REG", "TM2_REG", "TMCT"]):
            advanced_features += 8
            positives.append("Uses timer functionality")

        # ADC usage
        if "ADC_REG" in code:
            advanced_features += 8
            positives.append("Uses ADC functionality")

        # UART usage
        if any(uart in code for uart in ["TX_DAT", "RX_DAT", "COM_REG"]):
            advanced_features += 8
            positives.append("Uses UART communication")

        # Mathematical operations
        if any(math in code for math in ["ADD", "SUB", "MUL", "DIV", "INC", "DEC"]):
            advanced_features += 6
            positives.append("Uses mathematical operations")

        score += min(advanced_features, 30)

        # Expected features implementation (20 points)
        implemented_features = 0
        for feature in test_case.expected_features:
            if self._check_feature_implementation(feature, code):
                implemented_features += 1

        feature_score = (implemented_features / len(test_case.expected_features)) * 20
        score += feature_score
        positives.append(f"Implements {implemented_features}/{len(test_case.expected_features)} expected features")

        # Compilation bonus
        if test_case.compilation_success:
            positives.append("Code compiles successfully")
        else:
            issues.append("Compilation failed")
            score = max(0, score - 10)  # Penalty for compilation failure

        # Construct review result
        strengths = "Strengths: " + ", ".join(positives) if positives else ""
        problems = "Issues: " + ", ".join(issues) if issues else ""

        review_parts = [p for p in [strengths, problems] if p]
        review_result = ". ".join(review_parts) + "."

        return review_result, min(100, max(0, int(score)))

    def _check_feature_implementation(self, feature: str, code: str) -> bool:
        """Enhanced feature checking for new test cases"""
        feature_lower = feature.lower()

        # New feature checks for second round
        if "pwm" in feature_lower:
            return any(pattern in code for pattern in ["JUMP", "JZ"]) and "LDINS" in code

        elif "timer" in feature_lower:
            return any(timer in code for timer in ["TM0_REG", "TM1_REG", "TM2_REG", "TMCT"])

        elif "edge detection" in feature_lower or "state change" in feature_lower:
            return "LD IO" in code and any(cmp in code for cmp in ["JZ", "SUB", "ADD"])

        elif "frequency" in feature_lower or "square wave" in feature_lower:
            return "JUMP" in code and "LDINS" in code

        elif "maximum" in feature_lower or "comparison" in feature_lower:
            return any(cmp in code for cmp in ["SUB", "JZ", "JOV"])

        elif "filtering" in feature_lower or "moving average" in feature_lower:
            return "ADD" in code and "MUL" in code or "DIV" in code

        elif "combination" in feature_lower or "multi-button" in feature_lower:
            return "AND" in code or "OR" in code

        elif "uart" in feature_lower or "communication" in feature_lower:
            return any(uart in code for uart in ["TX_DAT", "RX_DAT", "COM_REG"])

        elif "scheduling" in feature_lower or "multi-task" in feature_lower:
            return code.count("JUMP") > 3 and ":" in code

        elif "pid" in feature_lower or "control algorithm" in feature_lower:
            return "MUL" in code and "SUB" in code and "ADD" in code

        # Fallback to original feature checking
        return self._original_feature_check(feature_lower, code)

    def _original_feature_check(self, feature_lower: str, code: str) -> bool:
        """Original feature checking logic"""
        data_section = code.split("ENDDATA")[0] if "ENDDATA" in code else ""

        if "ioset0" in feature_lower or "configuration" in feature_lower:
            return "IOSET0" in data_section
        elif "io pin" in feature_lower or "pin control" in feature_lower:
            return "IO" in data_section and "ST IO" in code
        elif "delay" in feature_lower or "timing" in feature_lower:
            return any(pattern in code for pattern in ["DEC", "JZ", "JUMP"]) and "LDINS" in code
        elif "adc" in feature_lower:
            return "ADC_REG" in data_section or "ADC" in code
        else:
            return False

    def run_all_tests(self):
        """Run all new test cases"""
        print("🚀 Starting NEW MCU-Copilot LLM System Test Suite - Round 2")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total New Test Cases: {len(self.test_cases)}")

        for test_case in self.test_cases:
            self.run_test_case(test_case)
            self.results.append(test_case)

        print(f"\n{'='*60}")
        print("🏁 NEW Test Suite Completed")
        print('='*60)

        # Generate summary
        self._print_summary()
        # Generate detailed report
        report_filename = self._generate_html_report()
        print(f"📄 Detailed report saved to: {report_filename}")
        print(f"\n🎯 NEW Test Suite Complete!")
        print("Check the generated HTML report for detailed analysis.")

    def _print_summary(self):
        """Print test summary"""
        total_cases = len(self.results)
        compilation_successes = sum(1 for r in self.results if r.compilation_success)
        success_rate = (compilation_successes / total_cases) * 100 if total_cases > 0 else 0

        scores = [r.review_score for r in self.results if r.review_score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Category breakdown
        simple_scores = [r.review_score for r in self.results if r.category == "simple" and r.review_score > 0]
        medium_scores = [r.review_score for r in self.results if r.category == "medium" and r.review_score > 0]
        complex_scores = [r.review_score for r in self.results if r.category == "complex" and r.review_score > 0]

        print(f"\n📈 NEW Test Summary:")
        print(f"   Total Cases: {total_cases}")
        print(f"   Compilation Success: {compilation_successes}/{total_cases} ({success_rate:.1f}%)")
        print(f"   Average Review Score: {avg_score:.1f}/100")

        if simple_scores:
            print(f"   Simple Cases Average: {sum(simple_scores)/len(simple_scores):.1f}/100")
        if medium_scores:
            print(f"   Medium Cases Average: {sum(medium_scores)/len(medium_scores):.1f}/100")
        if complex_scores:
            print(f"   Complex Cases Average: {sum(complex_scores)/len(complex_scores):.1f}/100")

        # Best and worst performers
        if self.results:
            best_result = max(self.results, key=lambda x: x.review_score)
            worst_result = min(self.results, key=lambda x: x.review_score)
            print(f"\n🏆 Best Performance: {best_result.id} ({best_result.review_score}/100)")
            print(f"🔧 Needs Improvement: {worst_result.id} ({worst_result.review_score}/100)")

    def _generate_html_report(self) -> str:
        """Generate enhanced HTML report with proper formatting"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"NEW_MCU_Copilot_Test_Report_{timestamp}.html"

        # Calculate statistics
        total_cases = len(self.results)
        compilation_successes = sum(1 for r in self.results if r.compilation_success)
        success_rate = (compilation_successes / total_cases) * 100 if total_cases > 0 else 0

        scores = [r.review_score for r in self.results if r.review_score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEW MCU-Copilot LLM System Test Report - Round 2</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #059669; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .header .meta {{ margin-top: 10px; opacity: 0.9; }}
        .summary {{ padding: 30px; border-bottom: 1px solid #e5e7eb; }}
        .stats {{ display: flex; gap: 20px; margin-top: 20px; }}
        .stat {{ text-align: center; padding: 20px; background: #f3f4f6; border-radius: 6px; flex: 1; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #1f2937; }}
        .stat-label {{ color: #6b7280; margin-top: 5px; }}
        .test-case {{ margin: 20px; border: 1px solid #d1d5db; border-radius: 6px; overflow: hidden; }}
        .test-header {{ background: #f9fafb; padding: 15px; border-bottom: 1px solid #e5e7eb; }}
        .test-id {{ font-weight: bold; color: #1f2937; }}
        .test-category {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
        .simple {{ background: #dbeafe; color: #1d4ed8; }}
        .medium {{ background: #fef3c7; color: #d97706; }}
        .complex {{ background: #fecaca; color: #dc2626; }}
        .test-content {{ padding: 20px; }}
        .requirement {{ background: #f0f9ff; padding: 15px; border-radius: 4px; border-left: 4px solid #0ea5e9; margin-bottom: 20px; }}
        .result-section {{ margin: 15px 0; }}
        .result-section h4 {{ margin: 0 0 10px 0; color: #374151; }}
        .code-block {{ background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 400px; overflow-y: auto; line-height: 1.4; }}
        .success {{ color: #059669; }}
        .error {{ color: #dc2626; }}
        .score {{ font-size: 1.2em; font-weight: bold; }}
        .score-excellent {{ color: #059669; }}
        .score-good {{ color: #0891b2; }}
        .score-fair {{ color: #d97706; }}
        .score-poor {{ color: #dc2626; }}
        .review {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 15px; }}
        .new-badge {{ background: #059669; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 NEW MCU-Copilot Test Report - Round 2</h1>
            <div class="meta">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                <span class="new-badge">10 NEW TEST CASES</span> |
                ZH5001 FPGA Advanced Features
            </div>
        </div>

        <div class="summary">
            <h2>📊 NEW Test Summary</h2>
            <p><strong>🔬 Round 2 Testing:</strong> This report tests 10 NEW diverse test cases including advanced features like PWM, timers, UART communication, PID control, and multi-tasking.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_cases}</div>
                    <div class="stat-label">NEW Test Cases</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{compilation_successes}/{total_cases}</div>
                    <div class="stat-label">Compilation Success</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_score:.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
            </div>
        </div>
"""

        # Add individual test cases with proper code formatting
        for result in self.results:
            score_class = self._get_score_class(result.review_score)

            # Convert assembly code to proper HTML format
            truncated_asm = result.generated_asm[:1000] + "..." if len(result.generated_asm) > 1000 else result.generated_asm
            # Convert \n literal strings to actual newlines, then to HTML
            asm_display = truncated_asm.replace('\\n', '\n').replace('\n', '<br>')

            html += f"""
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">NEW Test Case {result.id}</span>
                <span class="test-category {result.category}">{result.category.upper()}</span>
                <span class="score {score_class}" style="float: right;">{result.review_score}/100</span>
            </div>
            <div class="test-content">
                <div class="requirement">
                    <strong>Requirement:</strong> {result.requirement}
                </div>
                <div class="result-section">
                    <h4>Expected Features</h4>
                    <ul>{"".join(f"<li>{feature}</li>" for feature in result.expected_features)}</ul>
                </div>
                <div class="result-section">
                    <h4>Generated Assembly Code</h4>
                    <div class="code-block">{asm_display}</div>
                </div>
                <div class="result-section">
                    <h4>Compilation Result</h4>"""

            if result.compilation_success:
                html += f'<p class="success">✅ Compilation Successful</p>'
            else:
                html += f'<p class="error">❌ Compilation Failed</p>'
                if result.compilation_errors:
                    html += '<div class="error-list">'
                    for error in result.compilation_errors[:5]:  # Show first 5 errors
                        html += f'<div class="error-item">{error}</div>'
                    html += '</div>'

            html += f"""
                </div>
                <div class="result-section">
                    <h4>Code Review & Analysis</h4>
                    <div class="review">
                        <strong>Score:</strong> <span class="score {score_class}">{result.review_score}/100</span><br>
                        <strong>Analysis:</strong> {result.review_result}
                    </div>
                </div>
            </div>
        </div>"""

        html += """
    </div>
</body>
</html>"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        return filename

    def _get_score_class(self, score: int) -> str:
        """Get CSS class based on score"""
        if score >= 80:
            return "score-excellent"
        elif score >= 60:
            return "score-good"
        elif score >= 40:
            return "score-fair"
        else:
            return "score-poor"

if __name__ == "__main__":
    print("Initializing NEW MCU-Copilot Test Suite - Round 2...")
    suite = NewMCUTestSuite()
    suite.run_all_tests()
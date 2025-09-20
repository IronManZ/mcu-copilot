#!/usr/bin/env python3
"""
Comprehensive Test Cases for MCU-Copilot LLM System

This script tests the enhanced LLM system with 10 test cases (5 simple + 5 medium)
and generates a detailed test report with compilation verification.
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
        self.category = category  # "simple" or "medium"
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

class MCUTestSuite:
    def __init__(self):
        # Initialize configuration for nl_to_assembly_v2
        self._init_config()
        self.compiler = ZH5001CompilerService()
        self.test_cases = self._define_test_cases()
        self.results = []

    def _init_config(self):
        """Initialize LLM configuration"""
        if not config_manager.get_all_llm_configs():
            config_manager._parse_config_data(get_default_config())
            config_manager._load_from_environment()

    def _define_test_cases(self) -> list[TestCase]:
        """Define the 10 test cases (5 simple + 5 medium)"""

        simple_cases = [
            TestCase(
                id="S1",
                category="simple",
                requirement="控制P00引脚的LED灯闪烁",
                expected_features=["IOSET0 configuration", "IO pin control", "delay loop", "LED toggle"]
            ),
            TestCase(
                id="S2",
                category="simple",
                requirement="读取P01引脚的按键状态并输出到P02",
                expected_features=["input configuration", "button reading", "output control", "simple I/O transfer"]
            ),
            TestCase(
                id="S3",
                category="simple",
                requirement="在数码管上显示数字5",
                expected_features=["7-segment display", "segment pattern", "static display", "I/O output"]
            ),
            TestCase(
                id="S4",
                category="simple",
                requirement="实现一个简单的计数器，从0计数到9然后重复",
                expected_features=["counter variable", "increment logic", "overflow handling", "loop structure"]
            ),
            TestCase(
                id="S5",
                category="simple",
                requirement="检测ADC通道0的模拟输入值",
                expected_features=["ADC configuration", "channel selection", "conversion start", "result reading"]
            )
        ]

        medium_cases = [
            TestCase(
                id="M1",
                category="medium",
                requirement="数码管显示0-9循环，每秒切换一次数字",
                expected_features=["digit table", "MOVC instruction", "timing control", "display cycling", "LDTAB usage"]
            ),
            TestCase(
                id="M2",
                category="medium",
                requirement="按键控制LED：按下P00按键时P01 LED亮，松开时灭，带按键消抖",
                expected_features=["button debounce", "state detection", "conditional control", "input/output coordination"]
            ),
            TestCase(
                id="M3",
                category="medium",
                requirement="多路ADC采集：轮询检测ADC通道0-3，将结果显示在数码管上",
                expected_features=["multi-channel ADC", "channel switching", "polling loop", "result display", "data conversion"]
            ),
            TestCase(
                id="M4",
                category="medium",
                requirement="跑马灯效果：8个LED（P00-P07）依次点亮，产生流水灯效果",
                expected_features=["bit shifting", "pattern generation", "timing control", "multi-LED control", "sequential activation"]
            ),
            TestCase(
                id="M5",
                category="medium",
                requirement="双数码管显示：同时显示十位和个位数字，实现00-99的计数显示",
                expected_features=["dual digit control", "BCD conversion", "digit separation", "synchronized display", "two-digit arithmetic"]
            )
        ]

        return simple_cases + medium_cases

    def run_test_case(self, test_case: TestCase):
        """Execute a single test case"""
        print(f"\n{'='*60}")
        print(f"Running Test Case {test_case.id}: {test_case.category.upper()}")
        print(f"Requirement: {test_case.requirement}")
        print('='*60)

        try:
            # Generate assembly code using nl_to_assembly_v2 system
            print("🔄 Generating assembly code...")
            thought, assembly = nl_to_assembly_service.generate_assembly(
                requirement=test_case.requirement,
                session_id=f"test_{test_case.id}"
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
        """Review the generated assembly code and assign a score"""

        if not test_case.generated_asm:
            return "No assembly code generated.", 0

        score = 0
        issues = []
        positives = []

        code = test_case.generated_asm.upper()

        # Check basic structure (20 points)
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

        # Check variable definitions (15 points)
        data_section = ""
        if "DATA" in code and "ENDDATA" in code:
            start = code.find("DATA") + 4
            end = code.find("ENDDATA")
            data_section = code[start:end]

            if any(reg in data_section for reg in ["IOSET0", "IO"]):
                score += 15
                positives.append("Properly defines I/O registers")
            else:
                issues.append("Missing essential I/O register definitions")

        # Check instruction usage (25 points)
        essential_found = 0

        if "LDINS" in code:
            essential_found += 1
            positives.append("Uses LDINS for immediate values")

        if any(instr in code for instr in ["LD ", "ST "]):
            essential_found += 1
            positives.append("Uses load/store instructions")

        if test_case.category == "simple":
            if essential_found >= 2:
                score += 25
        else:  # medium cases need more sophisticated instructions
            if essential_found >= 2 and any(instr in code for instr in ["ADD", "SUB", "AND", "OR", "MOVC", "LDTAB"]):
                score += 25
                positives.append("Uses advanced instructions appropriately")
            elif essential_found >= 2:
                score += 15

        # Check feature implementation (25 points)
        features_implemented = 0
        for feature in test_case.expected_features:
            if self._check_feature_implementation(feature, code, data_section):
                features_implemented += 1

        feature_score = min(25, (features_implemented / len(test_case.expected_features)) * 25)
        score += int(feature_score)

        if features_implemented > 0:
            positives.append(f"Implements {features_implemented}/{len(test_case.expected_features)} expected features")

        # Check compilation success (15 points)
        if test_case.compilation_success:
            score += 15
            positives.append("Code compiles successfully")
        else:
            issues.append("Code has compilation errors")
            # Partial credit for minor issues
            if len(test_case.compilation_errors) <= 2:
                score += 5

        # Generate review summary
        review_parts = []

        if positives:
            review_parts.append(f"Strengths: {', '.join(positives)}")

        if issues:
            review_parts.append(f"Issues: {', '.join(issues)}")

        # Add specific recommendations
        recommendations = []

        if not test_case.compilation_success:
            recommendations.append("fix compilation errors")

        if "IOSET0" not in data_section and any(feature in ["LED", "button", "I/O"] for feature in str(test_case.expected_features)):
            recommendations.append("add I/O configuration")

        if test_case.category == "medium" and "MOVC" not in code and "display" in test_case.requirement.lower():
            recommendations.append("consider using lookup tables with MOVC")

        if recommendations:
            review_parts.append(f"Recommendations: {', '.join(recommendations)}")

        review_text = ". ".join(review_parts) + "."

        return review_text, min(100, score)

    def _check_feature_implementation(self, feature: str, code: str, data_section: str) -> bool:
        """Check if a specific feature is implemented in the code"""

        feature_lower = feature.lower()
        code_lower = code.lower()

        if "ioset0" in feature_lower:
            return "IOSET0" in data_section and "ST IOSET0" in code

        elif "io pin" in feature_lower or "led" in feature_lower:
            return "IO" in data_section and "ST IO" in code

        elif "delay" in feature_lower or "timing" in feature_lower:
            return any(pattern in code for pattern in ["DEC", "JZ", "JUMP"]) and "LDINS" in code

        elif "button" in feature_lower or "input" in feature_lower:
            return "LD IO" in code

        elif "7-segment" in feature_lower or "display" in feature_lower:
            return "0X1" in code or "0X0" in code  # Check for segment patterns

        elif "counter" in feature_lower or "increment" in feature_lower:
            return "INC" in code or "ADD" in code

        elif "adc" in feature_lower:
            return "ADC_REG" in data_section and "ADC" in code

        elif "movc" in feature_lower or "ldtab" in feature_lower:
            return "MOVC" in code or "LDTAB" in code

        elif "loop" in feature_lower:
            return ":" in code and ("JZ" in code or "JUMP" in code)

        elif "debounce" in feature_lower:
            return "DEC" in code and "JZ" in code  # Simple debounce check

        elif "multi-channel" in feature_lower:
            return "ADC" in code and ("ADD" in code or "INC" in code)

        elif "shifting" in feature_lower or "pattern" in feature_lower:
            return any(shift in code for shift in ["SFT0LZ", "SFT0RZ", "SFT1LZ"])

        elif "dual" in feature_lower or "two-digit" in feature_lower:
            return code.count("ST IO") > 1 or "MUL" in code or "DIV" in code

        return False

    def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting MCU-Copilot LLM System Test Suite")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total Test Cases: {len(self.test_cases)}")

        for test_case in self.test_cases:
            self.run_test_case(test_case)
            self.results.append(test_case)

        print(f"\n{'='*60}")
        print("🏁 Test Suite Completed")
        print('='*60)

        # Generate summary
        self._print_summary()

        # Generate detailed report
        report_file = self._generate_detailed_report()
        print(f"\n📄 Detailed report saved to: {report_file}")

        return self.results

    def _print_summary(self):
        """Print test summary"""

        total = len(self.results)
        compiled = sum(1 for r in self.results if r.compilation_success)
        simple_cases = [r for r in self.results if r.category == "simple"]
        medium_cases = [r for r in self.results if r.category == "medium"]

        avg_score = sum(r.review_score for r in self.results) / total if total > 0 else 0
        simple_avg = sum(r.review_score for r in simple_cases) / len(simple_cases) if simple_cases else 0
        medium_avg = sum(r.review_score for r in medium_cases) / len(medium_cases) if medium_cases else 0

        print(f"\n📈 Test Summary:")
        print(f"   Total Cases: {total}")
        print(f"   Compilation Success: {compiled}/{total} ({compiled/total*100:.1f}%)")
        print(f"   Average Review Score: {avg_score:.1f}/100")
        print(f"   Simple Cases Average: {simple_avg:.1f}/100")
        print(f"   Medium Cases Average: {medium_avg:.1f}/100")

        # Show best and worst cases
        best_case = max(self.results, key=lambda x: x.review_score)
        worst_case = min(self.results, key=lambda x: x.review_score)

        print(f"\n🏆 Best Performance: {best_case.id} ({best_case.review_score}/100)")
        print(f"🔧 Needs Improvement: {worst_case.id} ({worst_case.review_score}/100)")

    def _generate_detailed_report(self) -> str:
        """Generate detailed HTML test report"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"MCU_Copilot_Test_Report_{timestamp}.html"

        html_content = self._build_html_report()

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_file

    def _build_html_report(self) -> str:
        """Build comprehensive HTML report"""

        # Calculate statistics
        total = len(self.results)
        compiled = sum(1 for r in self.results if r.compilation_success)
        avg_score = sum(r.review_score for r in self.results) / total if total > 0 else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCU-Copilot LLM System Test Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #2563eb; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
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
        .test-content {{ padding: 20px; }}
        .requirement {{ background: #f0f9ff; padding: 15px; border-radius: 4px; border-left: 4px solid #0ea5e9; margin-bottom: 20px; }}
        .result-section {{ margin: 15px 0; }}
        .result-section h4 {{ margin: 0 0 10px 0; color: #374151; }}
        .code-block {{ background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 300px; overflow-y: auto; }}
        .success {{ color: #059669; }}
        .error {{ color: #dc2626; }}
        .warning {{ color: #d97706; }}
        .score {{ font-size: 1.2em; font-weight: bold; }}
        .score-excellent {{ color: #059669; }}
        .score-good {{ color: #0891b2; }}
        .score-fair {{ color: #d97706; }}
        .score-poor {{ color: #dc2626; }}
        .error-list {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 4px; padding: 10px; }}
        .error-item {{ color: #991b1b; margin: 5px 0; }}
        .review {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 4px; padding: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCU-Copilot LLM System Test Report</h1>
            <div class="meta">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                Enhanced Prompt Template | ZH5001 FPGA Development Board
            </div>
        </div>

        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total}</div>
                    <div class="stat-label">Total Test Cases</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{compiled}/{total}</div>
                    <div class="stat-label">Compilation Success</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{compiled/total*100:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_score:.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
            </div>
        </div>"""

        # Add individual test cases
        for result in self.results:
            score_class = self._get_score_class(result.review_score)

            # Truncate code for display and convert \n to proper HTML line breaks
            truncated_asm = result.generated_asm[:1000] + "..." if len(result.generated_asm) > 1000 else result.generated_asm
            # Convert \n literal strings to actual newlines, then to HTML
            asm_display = truncated_asm.replace('\\n', '\n').replace('\n', '<br>\n')

            html += f"""
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">Test Case {result.id}</span>
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
                    for error in result.compilation_errors:
                        html += f'<div class="error-item">• {error}</div>'
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

        return html

    def _get_score_class(self, score: int) -> str:
        """Get CSS class for score color coding"""
        if score >= 90:
            return "score-excellent"
        elif score >= 75:
            return "score-good"
        elif score >= 60:
            return "score-fair"
        else:
            return "score-poor"

def main():
    """Run the test suite"""

    # Set API key
    os.environ['QIANWEN_APIKEY'] = 'sk-345a0038bd2c45268f6a12f68614d318'

    print("Initializing MCU-Copilot Test Suite...")

    test_suite = MCUTestSuite()
    results = test_suite.run_all_tests()

    print("\n🎯 Test Suite Complete!")
    print("Check the generated HTML report for detailed analysis.")

if __name__ == "__main__":
    main()
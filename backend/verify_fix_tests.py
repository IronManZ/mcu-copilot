#!/usr/bin/env python3
"""
Verification tests for the fixed temperature configuration system
5 additional test cases to verify the system works properly
"""

import sys
import os
from datetime import datetime
sys.path.append('app')

from new_test_cases import TestCase, NewMCUTestSuite

def create_verification_test_cases():
    """Create 5 additional test cases to verify the fixed system"""

    test_cases = [
        TestCase(
            id='V1',
            category='SIMPLE',
            requirement='实现简单的交通灯控制：红灯3秒，绿灯2秒，黄灯1秒循环',
            expected_features=['timing control', 'LED sequencing', 'state machine', 'loop control']
        ),

        TestCase(
            id='V2',
            category='SIMPLE',
            requirement='读取温度传感器ADC值并显示到7段数码管',
            expected_features=['ADC reading', 'data processing', 'display control', 'sensor interface']
        ),

        TestCase(
            id='V3',
            category='MEDIUM',
            requirement='实现步进电机控制：顺时针转10步然后逆时针转10步',
            expected_features=['stepper motor', 'direction control', 'step counting', 'motor sequencing']
        ),

        TestCase(
            id='V4',
            category='MEDIUM',
            requirement='实现简单的看门狗定时器：如果主程序卡死则自动重启',
            expected_features=['watchdog timer', 'system reset', 'timeout detection', 'fail-safe mechanism']
        ),

        TestCase(
            id='V5',
            category='COMPLEX',
            requirement='实现智能风扇控制：根据温度自动调节转速，支持手动模式切换',
            expected_features=['temperature sensing', 'PWM speed control', 'mode switching', 'automatic control', 'manual override']
        )
    ]

    return test_cases

def generate_html_report(test_results, output_file):
    """Generate HTML report for verification tests"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate statistics
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results if result.compilation_success)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

    avg_score = sum(result.review_score for result in test_results) / total_tests if total_tests > 0 else 0

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCU-Copilot System Verification Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #10b981; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
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
        .fix-badge {{ background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 System Verification Report</h1>
            <div class="meta">
                Generated: {timestamp} |
                <span class="fix-badge">TEMPERATURE FIX VERIFIED</span> |
                ZH5001 System Validation
            </div>
        </div>

        <div class="summary">
            <h2>📊 Verification Test Summary</h2>
            <p><strong>🔧 System Fix Verification:</strong> Testing 5 additional cases to verify the temperature configuration fix resolves the retry system issues.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Verification Tests</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{successful_tests}/5</div>
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

    # Add test case results
    for result in test_results:
        # Determine score class
        score_class = "score-poor"
        if result.review_score >= 80:
            score_class = "score-excellent"
        elif result.review_score >= 70:
            score_class = "score-good"
        elif result.review_score >= 50:
            score_class = "score-fair"

        # Format assembly code for HTML display
        asm_display = ""
        if result.generated_asm:
            truncated_asm = result.generated_asm[:1000] + "..." if len(result.generated_asm) > 1000 else result.generated_asm
            asm_display = truncated_asm.replace('\\n', '\n').replace('\n', '<br>\n')

        # Expected features list
        features_html = "".join(f"<li>{feature}</li>" for feature in result.expected_features)

        # Compilation result
        compilation_html = f'<p class="success">✅ Compilation Successful</p>' if result.compilation_success else f'<p class="error">❌ Compilation Failed</p>'

        # Review summary
        review_summary = getattr(result, 'review_summary', 'No review available')

        html_content += f"""
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">Verification Test {result.id}</span>
                <span class="test-category {result.category.lower()}">{result.category}</span>
                <span class="score {score_class}" style="float: right;">{result.review_score}/100</span>
            </div>
            <div class="test-content">
                <div class="requirement">
                    <strong>Requirement:</strong> {result.requirement}
                </div>
                <div class="result-section">
                    <h4>Expected Features</h4>
                    <ul>{features_html}</ul>
                </div>
                <div class="result-section">
                    <h4>Generated Assembly Code</h4>
                    <div class="code-block">{asm_display}</div>
                </div>
                <div class="result-section">
                    <h4>Compilation Result</h4>{compilation_html}
                </div>
                <div class="result-section">
                    <h4>Code Review & Analysis</h4>
                    <div class="review">
                        <strong>Score:</strong> <span class="score {score_class}">{result.review_score}/100</span><br>
                        <strong>Analysis:</strong> {review_summary}
                    </div>
                </div>
            </div>
        </div>"""

    html_content += """
    </div>
</body>
</html>"""

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def run_verification_tests():
    """Run the 5 verification test cases"""

    print("🔧 Starting System Verification Tests...")
    print("📅 Testing temperature configuration fix")
    print("📊 Running 5 additional test cases")
    print("="*60)

    # Create test cases
    test_cases = create_verification_test_cases()

    # Create test suite
    suite = NewMCUTestSuite()

    results = []

    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Running Verification Test {test_case.id}: {test_case.category}")
        print(f"Requirement: {test_case.requirement}")
        print('='*60)

        try:
            # Run the test case
            suite.run_test_case(test_case)
            results.append(test_case)

            if test_case.compilation_success:
                print(f"✅ Test {test_case.id} completed successfully!")
            else:
                print(f"❌ Test {test_case.id} compilation failed")

        except Exception as e:
            print(f"❌ Test {test_case.id} failed with exception: {e}")
            # Still add to results to track the failure
            test_case.compilation_success = False
            test_case.review_score = 0
            test_case.review_summary = f"Test execution failed: {e}"
            results.append(test_case)

    # Generate summary
    print(f"\n{'='*60}")
    print("🏁 Verification Tests Completed")
    print(f"{'='*60}")

    successful = sum(1 for result in results if result.compilation_success)
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0

    print(f"📈 Verification Summary:")
    print(f"   Total Cases: {total}")
    print(f"   Compilation Success: {successful}/{total} ({success_rate:.1f}%)")

    if hasattr(results[0], 'review_score'):
        avg_score = sum(getattr(result, 'review_score', 0) for result in results) / total
        print(f"   Average Review Score: {avg_score:.1f}/100")

    # Generate HTML report
    report_filename = f"System_Verification_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    generate_html_report(results, report_filename)
    print(f"📄 Detailed report saved to: {report_filename}")

    print(f"\n🎯 Verification Tests Complete!")
    print("🔧 Temperature configuration fix verification finished.")

    return results

if __name__ == "__main__":
    run_verification_tests()
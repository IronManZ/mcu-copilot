#!/usr/bin/env python3
"""
Gemini API Verification Tests - Testing 5 cases with working Gemini provider
"""

import sys
import os
from datetime import datetime
sys.path.append('app')

from new_test_cases import TestCase, NewMCUTestSuite

def create_gemini_test_cases():
    """Create 5 test cases specifically for Gemini verification"""

    test_cases = [
        TestCase(
            id='G1',
            category='SIMPLE',
            requirement='控制LED P03引脚闪烁：500ms开，500ms关',
            expected_features=['LED control', 'timing delay', 'pin toggle', 'loop control']
        ),

        TestCase(
            id='G2',
            category='SIMPLE',
            requirement='读取按键P01状态：按下时点亮LED P05',
            expected_features=['input reading', 'conditional control', 'LED output', 'button interface']
        ),

        TestCase(
            id='G3',
            category='MEDIUM',
            requirement='实现计数器：每按一次P02按键，LED P04闪烁次数加1',
            expected_features=['counter logic', 'button counting', 'variable LED flashes', 'state management']
        ),

        TestCase(
            id='G4',
            category='MEDIUM',
            requirement='ADC采集P06引脚电压：大于阈值时蜂鸣器响',
            expected_features=['ADC reading', 'threshold comparison', 'buzzer control', 'analog processing']
        ),

        TestCase(
            id='G5',
            category='COMPLEX',
            requirement='实现简单状态机：空闲->采集->处理->输出四个状态循环',
            expected_features=['state machine', 'state transitions', 'multi-stage processing', 'control flow', 'system design']
        )
    ]

    return test_cases

def run_gemini_verification():
    """Run verification tests with Gemini API"""

    print("🚀 Starting Gemini API Verification Tests")
    print("📅 Testing with Gemini 1.5-Flash model")
    print("🔑 Using configured API key")
    print("="*60)

    # Create test cases
    test_cases = create_gemini_test_cases()

    # Create test suite
    suite = NewMCUTestSuite()

    results = []

    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Running Gemini Test {test_case.id}: {test_case.category}")
        print(f"Requirement: {test_case.requirement}")
        print('='*60)

        try:
            # Set environment variable for Gemini
            os.environ['GEMINI_API_KEY'] = 'AIzaSyBhcJQYnSqO7uuQeCQo2qig3IO69CvgAOg'

            # Run the test case
            suite.run_test_case(test_case)
            results.append(test_case)

            if test_case.compilation_success:
                print(f"✅ Test {test_case.id} completed successfully!")
                print(f"📊 Review Score: {getattr(test_case, 'review_score', 'N/A')}/100")
            else:
                print(f"❌ Test {test_case.id} compilation failed")
                print(f"🔍 Errors: {len(test_case.compilation_errors)}")

        except Exception as e:
            print(f"❌ Test {test_case.id} failed with exception: {e}")
            # Still add to results to track the failure
            test_case.compilation_success = False
            test_case.review_score = 0
            test_case.generated_asm = ""
            results.append(test_case)

    # Generate summary
    print(f"\n{'='*60}")
    print("🏁 Gemini Verification Tests Completed")
    print(f"{'='*60}")

    successful = sum(1 for result in results if result.compilation_success)
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0

    print(f"📈 Gemini Test Summary:")
    print(f"   Total Cases: {total}")
    print(f"   Compilation Success: {successful}/{total} ({success_rate:.1f}%)")

    if any(hasattr(r, 'review_score') for r in results):
        avg_score = sum(getattr(r, 'review_score', 0) for r in results) / total
        print(f"   Average Review Score: {avg_score:.1f}/100")

    print(f"\n🔍 Individual Results:")
    for result in results:
        status = "✅" if result.compilation_success else "❌"
        score = getattr(result, 'review_score', 0)
        print(f"  {result.id}: {status} {result.category} - Score: {score}/100")

    # Generate HTML report
    generate_gemini_html_report(results)

    return results

def generate_gemini_html_report(test_results):
    """Generate HTML report for Gemini verification tests"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"Gemini_Verification_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # Calculate statistics
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results if result.compilation_success)
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    avg_score = sum(getattr(result, 'review_score', 0) for result in test_results) / total_tests if total_tests > 0 else 0

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini API Verification Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: #4285f4; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
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
        .gemini-badge {{ background: #4285f4; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Gemini API Verification Report</h1>
            <div class="meta">
                Generated: {timestamp} |
                <span class="gemini-badge">GEMINI 1.5-FLASH</span> |
                MCU Assembly Code Generation
            </div>
        </div>

        <div class="summary">
            <h2>📊 Gemini Performance Summary</h2>
            <p><strong>🚀 API Integration Test:</strong> Testing Gemini 1.5-Flash for ZH5001 MCU assembly code generation, comparing performance vs broken Qwen API.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Gemini Test Cases</div>
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
        score = getattr(result, 'review_score', 0)
        score_class = "score-poor"
        if score >= 80:
            score_class = "score-excellent"
        elif score >= 70:
            score_class = "score-good"
        elif score >= 50:
            score_class = "score-fair"

        # Format assembly code for HTML display
        asm_display = ""
        if hasattr(result, 'generated_asm') and result.generated_asm:
            truncated_asm = result.generated_asm[:1000] + "..." if len(result.generated_asm) > 1000 else result.generated_asm
            asm_display = truncated_asm.replace('\\n', '\n').replace('\n', '<br>\n')

        # Expected features list
        features_html = "".join(f"<li>{feature}</li>" for feature in result.expected_features)

        # Compilation result
        compilation_html = f'<p class="success">✅ Compilation Successful</p>' if result.compilation_success else f'<p class="error">❌ Compilation Failed</p>'

        # Review summary
        review_summary = getattr(result, 'review_summary', 'Code review pending')

        html_content += f"""
        <div class="test-case">
            <div class="test-header">
                <span class="test-id">Gemini Test {result.id}</span>
                <span class="test-category {result.category.lower()}">{result.category}</span>
                <span class="score {score_class}" style="float: right;">{score}/100</span>
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
                        <strong>Score:</strong> <span class="score {score_class}">{score}/100</span><br>
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
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"📄 Gemini verification report saved to: {filename}")
    return filename

if __name__ == "__main__":
    # Run Gemini verification tests
    results = run_gemini_verification()

    print(f"\n🎯 Gemini API Integration Complete!")
    if results:
        success_count = sum(1 for r in results if r.compilation_success)
        print(f"🚀 Results: {success_count}/{len(results)} tests successful with Gemini")
        if success_count > 0:
            print(f"✅ Gemini API is working as replacement for broken Qwen!")
        else:
            print(f"⚠️  Gemini API needs further investigation")

    print(f"📊 Check HTML report for detailed analysis")
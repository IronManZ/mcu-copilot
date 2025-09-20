#!/usr/bin/env python3
"""Test a single case to verify the temperature fix works"""

import sys
sys.path.append('app')

from new_test_cases import TestCase, NewMCUTestSuite

def test_single_case():
    print("🧪 Testing single case with fixed temperature configuration...")

    # Create a simple test case
    test_case = TestCase(
        id='TEST',
        category='SIMPLE',
        requirement='控制LED P03引脚闪烁',
        expected_features=['LED control', 'pin toggle', 'timing']
    )

    # Create test suite
    suite = NewMCUTestSuite()

    try:
        # Run the single test case
        suite.run_test_case(test_case)
        result = test_case

        print(f"✅ Test completed successfully!")
        print(f"📊 Result: compilation_success={result.compilation_success}")
        print(f"📝 Generated ASM length: {len(result.generated_asm) if result.generated_asm else 0}")
        print(f"❌ Errors: {len(result.compilation_errors)}")

        if result.compilation_errors:
            print("First few errors:")
            for i, error in enumerate(result.compilation_errors[:3], 1):
                print(f"  {i}. {error}")

        return result

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    test_single_case()
#!/usr/bin/env python3
"""
Debug script to isolate the compilation validation bug
"""

import sys
sys.path.append('app')

from services.compiler.zh5001_service import ZH5001CompilerService

# The exact code from the HTML report that should fail
problem_code = '''DATA
PWM_PERIOD 48
PWM_DUTY 24
ENDDATA

CODE
main:
IOSET0 49 # Configure P03 as output
LDINS 0 # Clear R0

loop:
LD PWM_PERIOD
ST 48 # Store period in system register
LD PWM_DUTY
ST 49 # Store duty cycle in system register

LD 48
SUB 49 # Subtract duty cycle from period
JZ 50 # If zero, skip delay

delay_loop:
DEC # Decrement R0
JZ delay_loop # Loop until R0 is zero

LD 49
SUB 48 # Subtract duty cycle from period
JZ 50 # If zero, skip delay

delay_loop_duty:
DEC # Decrement R0
JZ delay_loop_duty # Loop until R0 is zero

JUMP loop # Go back to start of loop

50:
JUMP main # Infinite loop at the end
ENDCODE'''

def debug_compilation():
    print("🔍 DEBUG: Testing compilation validation")

    # Test 1: Direct compiler service
    print("\n1️⃣ Direct ZH5001CompilerService test:")
    compiler = ZH5001CompilerService()
    result = compiler.compile_assembly(problem_code)

    print(f"   Success: {result.get('success')}")
    print(f"   Error count: {len(result.get('errors', []))}")
    if result.get('errors'):
        print("   First few errors:")
        for i, error in enumerate(result['errors'][:3], 1):
            print(f"   {i}. {error}")

    # Test 2: Check if there are multiple compiler instances
    print("\n2️⃣ Second compiler instance test:")
    compiler2 = ZH5001CompilerService()
    result2 = compiler2.compile_assembly(problem_code)

    print(f"   Success: {result2.get('success')}")
    print(f"   Same result: {result == result2}")

    # Test 3: Simple valid code to ensure compiler works
    print("\n3️⃣ Testing with known valid code:")
    valid_code = '''DATA
    COUNT  0
ENDDATA

CODE
main:
    LDINS  1
    ST     COUNT
    LD     COUNT
    IO     49
ENDCODE'''

    valid_result = compiler.compile_assembly(valid_code)
    print(f"   Valid code success: {valid_result.get('success')}")
    print(f"   Valid code errors: {len(valid_result.get('errors', []))}")

    return result.get('success'), result.get('errors', [])

if __name__ == "__main__":
    success, errors = debug_compilation()
    print(f"\n🎯 FINAL RESULT: success={success}, errors={len(errors)}")
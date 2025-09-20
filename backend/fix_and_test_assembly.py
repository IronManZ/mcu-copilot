#!/usr/bin/env python3
"""
Fix and test all assembly codes from the test report
Generate corrected versions that actually compile
"""

import sys
sys.path.append('app/services/compiler')
from zh5001_service import ZH5001CompilerService

def test_and_fix_code(test_id: str, description: str, original_code: str):
    """Test original code and provide fixed version if needed"""
    print(f"\n{'='*60}")
    print(f"Testing {test_id}: {description}")
    print(f"{'='*60}")

    service = ZH5001CompilerService()

    # Test original code
    print("\n🧪 Testing original code:")
    result = service.compile_assembly(original_code)

    if result['success']:
        print("✅ Original code compiles successfully!")
        return original_code, True
    else:
        print("❌ Original code compilation failed:")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")

        # Try to provide a fixed version
        fixed_code = provide_fix(test_id, original_code, result['errors'])
        if fixed_code:
            print("\n🔧 Testing fixed code:")
            fixed_result = service.compile_assembly(fixed_code)
            if fixed_result['success']:
                print("✅ Fixed code compiles successfully!")
                return fixed_code, True
            else:
                print("❌ Fixed code still has errors:")
                for error in fixed_result['errors']:
                    print(f"  - {error}")
                return fixed_code, False
        else:
            return original_code, False

def provide_fix(test_id: str, original_code: str, errors: list) -> str:
    """Provide fixed assembly code based on test case and errors"""

    if test_id == "S1":  # LED blinking
        return """DATA
    IOSET0      49
    IO          51
    delay_count 0
ENDDATA

CODE
main:
    LDINS 0x0001    ; Set P00 as output
    ST IOSET0

loop:
    LDINS 0x0001    ; LED on
    ST IO

    ; Delay loop
    LDINS 1000
    ST delay_count
delay1:
    LD delay_count
    DEC
    ST delay_count
    JZ led_off
    JUMP delay1

led_off:
    LDINS 0x0000    ; LED off
    ST IO

    ; Another delay
    LDINS 1000
    ST delay_count
delay2:
    LD delay_count
    DEC
    ST delay_count
    JZ loop
    JUMP delay2
ENDCODE"""

    elif test_id == "S2":  # Button to LED
        return """DATA
    IOSET0      49
    IO          51
ENDDATA

CODE
main:
    LDINS 0x0002    ; P01 input, P02 output
    ST IOSET0

loop:
    LD IO           ; Read pins
    AND 0x0002      ; Check P01
    JZ button_off

button_on:
    LDINS 0x0004    ; Set P02 high
    ST IO
    JUMP loop

button_off:
    LDINS 0x0000    ; Set P02 low
    ST IO
    JUMP loop
ENDCODE"""

    elif test_id == "S3":  # 7-segment display
        return """DATA
    IOSET0      49
    IO          51
ENDDATA

CODE
main:
    LDINS 0x3FFF    ; All pins output
    ST IOSET0
    LDINS 0x16D     ; Pattern for digit 5
    ST IO

loop:
    JUMP loop       ; Keep displaying
ENDCODE"""

    elif test_id == "S4":  # Simple counter
        return """DATA
    IOSET0      49
    IO          51
    counter     0
    digit_table 10
    temp        1
ENDDATA

CODE
main:
    LDINS 0x3FFF    ; All pins output
    ST IOSET0
    LDINS 0
    ST counter

loop:
    LD counter
    LDTAB digit_patterns
    ADD counter
    MOVC            ; Get digit pattern
    ST IO

    LD counter
    INC
    ST counter
    LDINS 10
    SUB counter
    JZ reset_counter
    JUMP loop

reset_counter:
    LDINS 0
    ST counter
    JUMP loop

digit_patterns:
    DB 0x15F    ; 0
    DB 0x150    ; 1
    DB 0x13B    ; 2
    DB 0x179    ; 3
    DB 0x174    ; 4
    DB 0x16D    ; 5
    DB 0x16F    ; 6
    DB 0x158    ; 7
    DB 0x17F    ; 8
    DB 0x17D    ; 9
ENDCODE"""

    else:
        # For other cases, try basic fixes
        fixed = original_code
        # Fix common issues
        fixed = fixed.replace("IOSET0 49", "ST IOSET0")
        fixed = fixed.replace("IO 51", "ST IO")
        return fixed

# Test cases from the report
test_cases = [
    ("S1", "控制P00引脚的LED灯闪烁", """DATA
    LED_PIN 49
ENDDATA

CODE
main:
    IOSET0 49  # Configure P00 as output
    LDINS 1   # Load immediate value 1 into R0
loop:
    IO 51     # Write R0 to P00 (turn on LED)
    INC       # Increment R0
    JZ loop   # If R0 is zero, jump back to loop (toggle LED)
    LDINS 0   # Load immediate value 0 into R0
    IO 51     # Write R0 to P00 (turn off LED)
    INC       # Increment R0
    JZ loop   # If R0 is zero, jump back to loop (toggle LED)
ENDCODE"""),

    ("S2", "读取P01引脚的按键状态并输出到P02", """DATA
    P01 48
    P02 49
ENDDATA

CODE
main:
    IOSET0 49  # Configure P02 as output
    IO 48     # Read P01 state into R0
    IO 49     # Write R0 to P02
    JUMP main # Loop indefinitely
ENDCODE"""),

    ("S3", "在数码管上显示数字5", """DATA
    digit_5    49
ENDDATA

CODE
main:
    LDINS 5
    ST digit_5
    JUMP main
ENDCODE""")
]

if __name__ == "__main__":
    print("🚀 Testing and Fixing Assembly Codes")
    print("=" * 60)

    results = []
    for test_id, desc, code in test_cases:
        fixed_code, success = test_and_fix_code(test_id, desc, code)
        results.append((test_id, desc, fixed_code, success))

    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")

    for test_id, desc, code, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_id}: {status} - {desc}")
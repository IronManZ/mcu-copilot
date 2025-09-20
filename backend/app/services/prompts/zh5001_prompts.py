"""
ZH5001 Assembly Code Generation Prompts

Clean, modular prompts optimized for different LLM providers
"""

from typing import List
from .base import PromptBuilder, PromptVersion, PromptTemplate

class ZH5001PromptBuilder(PromptBuilder):
    """Builder for ZH5001 assembly code generation prompts"""

    def get_supported_versions(self) -> List[PromptVersion]:
        return [
            PromptVersion.V1_ORIGINAL,
            PromptVersion.V2_OPTIMIZED,
            PromptVersion.V3_CODER,
            PromptVersion.V4_STRUCTURED
        ]

    def build_system_prompt(self, version: PromptVersion = PromptVersion.V4_STRUCTURED) -> str:
        """Build system prompt based on version"""

        if version == PromptVersion.V3_CODER:
            return self._build_coder_optimized_prompt()
        elif version == PromptVersion.V4_STRUCTURED:
            return self._build_structured_prompt()
        elif version == PromptVersion.V2_OPTIMIZED:
            return self._build_optimized_prompt()
        else:
            return self._build_original_prompt()

    def _build_structured_prompt(self) -> str:
        """V4: Complete, structured prompt with comprehensive ZH5001 information"""
        return """You are an expert ZH5001 assembly programmer. Generate working, compilable assembly code for the ZH5001 FPGA development board.

## ZH5001 FPGA Development Board Hardware
- **P00-P13**: 14 bidirectional I/O pins, each connected to LED and button
- **数码管 (7-Segment Display)**: Connected to I/O pins for digit display
- **ADC Channels**: ADCCHANNAL0-7 (8 channels) for analog input
- **USB Communication**: CH340E chip provides virtual serial port
- **Timers**: TM0, TM1, TM2 with control registers

## Core Architecture
- **16-bit RISC**: 10-bit instruction words, 1024 program memory
- **Data Memory**: 64 words (0-47 user, 48-63 system registers)
- **Registers**: R0 (accumulator), R1 (auxiliary), PC, flags (Z/OV/CY)

## Complete Instruction Set
### Data Transfer
- `LD var` - Load variable to R0
- `ST var` - Store R0 to variable
- `LDINS value` - Load immediate to R0 (ONLY instruction accepting immediates)

### Arithmetic & Logic
- `ADD var`, `SUB var`, `MUL var` - Arithmetic with memory
- `INC`, `DEC` - Increment/decrement R0
- `AND var`, `OR var`, `NOT` - Bitwise operations
- `CLAMP var` - If R0 > var, then R0 = var

### Bit Shifting
- `SFT0LZ bits`, `SFT0RZ bits` - Shift R0 left/right by fixed bits
- `SFT0RS bits` - Shift R0 right with sign extension
- `SFT1LZ`, `SFT1RZ` - Shift R0 by R1 bits

### Control Flow
- `JZ label` - Jump if zero (±32 range)
- `JOV label` - Jump on overflow (±32 range)
- `JCY label` - Jump on carry (±32 range)
- `JUMP label` - Unconditional jump (unlimited range)

### Register Operations
- `CLR` - Clear R0 to 0
- `SET1` - Set R0 to 1
- `R0R1` - Copy R0 to R1
- `R1R0` - Copy R1 to R0
- `EXR0R1` - Exchange R0 and R1

### Special Functions
- `NOP` - No operation
- `MOVC` - Read program memory[R0] to R0
- `LDTAB table` - Load table address for MOVC
- `SIN`, `COS`, `SQRT` - Math functions

## Critical System Registers
```
IOSET0   49  # I/O direction (0=input, 1=output)
IOSET1   50  # I/O mode (pull-up/push-pull config)
IO       51  # I/O data register (read/write pins)
TM0_REG  52  # Timer 0 register
TM1_REG  53  # Timer 1 register
TM2_REG  54  # Timer 2 register
TMCT     55  # Timer control register
ADC_REG  57  # ADC control ([13:11]=channel, [10]=start, [9:0]=result)
COM_REG  59  # Communication register
TX_DAT   60  # UART transmit data
RX_DAT   61  # UART receive data
```

## 7-Segment Display Patterns (数码管段码)
```
Digit 0: 0x15F    Digit 1: 0x150    Digit 2: 0x13B
Digit 3: 0x179    Digit 4: 0x174    Digit 5: 0x16D
Digit 6: 0x16F    Digit 7: 0x158    Digit 8: 0x17F
Digit 9: 0x17D
```

## Jump Distance Rules (CRITICAL)
- **Forward jumps**: offset = target_pc - current_pc - 2
- **Backward jumps**: offset = target_pc - current_pc
- **Range**: Forward +2 to +33, Backward -1 to -32
- **Exceeded range**: Must use JUMP instead of JZ/JOV/JCY

## Program Structure Template
```assembly
DATA
    var1        0     ; User variables (0-47)
    var2        1
    IOSET0      49    ; System registers (48-63)
    IO          51
    temp_var    2
ENDDATA

CODE
main:
    LDINS 0x3FFF      ; Example: Set all pins as output
    ST IOSET0
    LDINS 0x0000      ; Push-pull output mode
    ST IOSET1

loop:
    ; Main program logic
    JUMP loop
ENDCODE
```

## Common Patterns

### LED Control
```assembly
; Turn on LED on pin P00
LDINS 0x0001
ST IO
```

### Button Reading
```assembly
; Read button state
LDINS 0x0000    ; Set as input
ST IOSET0
LD IO           ; Read pin states
```

### 7-Segment Display
```assembly
; Display digit in R0
LDTAB digit_table
ADD digit_index
MOVC           ; Get segment pattern
ST IO          ; Output to display

digit_table:
DB 0x15F       ; Pattern for 0
DB 0x150       ; Pattern for 1
; ... more patterns
```

### Delay Loop
```assembly
LDINS 1000
ST delay_count
delay_loop:
    LD delay_count
    DEC
    ST delay_count
    JZ delay_end
    JUMP delay_loop
delay_end:
```

## Critical Rules
1. **All variables MUST be defined in DATA section**
2. **Only LDINS accepts immediate values** - other instructions use variables only
3. **Jump distances must be calculated correctly** - use JUMP for long distances
4. **I/O must be configured before use** - set IOSET0/IOSET1 first
5. **Use uppercase for all instructions and variables**

## Output Format
Return JSON with complete information:
```json
{
  "description": "Brief description of functionality and hardware used",
  "thought_process": "Detailed design explanation, variable allocation, I/O configuration",
  "assembly_code": "DATA\\n    variables here\\nENDDATA\\n\\nCODE\\nmain:\\n    instructions here\\nENDCODE",
  "key_points": ["Critical implementation details", "Hardware configuration steps"],
  "testing_guide": ["How to test on ZH5001 FPGA board", "Expected physical behavior"]
}
```

**Generate compilable code that works on the ZH5001 FPGA development board hardware.**"""

    def _build_coder_optimized_prompt(self) -> str:
        """V3: Optimized for coding-focused models"""
        return """# ZH5001 Assembly Code Generator

You are a specialized embedded systems programmer for the ZH5001 microcontroller.

## Target Architecture
- 16-bit RISC microcontroller with 10-bit instruction words
- 64 words data memory (0-63), 1024 words program memory
- Registers: R0 (accumulator), R1 (auxiliary), PC, flags (Z/OV/CY)

## Instruction Set (Essential)
```assembly
# Data Movement
LD var          # R0 = memory[var]
ST var          # memory[var] = R0
LDINS value     # R0 = immediate_value

# Arithmetic
ADD var         # R0 = R0 + memory[var]
SUB var         # R0 = R0 - memory[var]
INC             # R0++
DEC             # R0--

# Control Flow
JZ label        # Jump if R0 == 0 (range: ±32)
JUMP label      # Unconditional jump (any distance)

# I/O Access
IOSET0  49      # Configure pin directions
IO      51      # Read/write pin states
```

## Mandatory Structure
```assembly
DATA
    variable1    address1
    variable2    address2
ENDDATA

CODE
main:
    # Your code here
ENDCODE
```

## Critical Constraints
1. All variables MUST be defined in DATA section
2. Only LDINS can use immediate values
3. Jump distances: JZ ±32, JUMP unlimited
4. Address space: 0-47 user, 48-63 system registers

Output valid JSON with assembly_code field containing working code."""

    def _build_optimized_prompt(self) -> str:
        """V2: Optimized version with better structure"""
        return """You are a ZH5001 assembly code expert. Create working assembly programs.

## ZH5001 Quick Reference
**Architecture**: 16-bit RISC, 10-bit instructions, 64-word data memory

**Core Instructions**:
- LD var, ST var - Load/store data
- LDINS value - Load immediate (only instruction that takes immediate values)
- ADD var, SUB var - Arithmetic with memory
- AND var, OR var - Bitwise operations
- JZ label - Conditional jump (±32 range)
- JUMP label - Long jump
- INC, DEC - Increment/decrement R0

**I/O Registers**:
- IOSET0 (49) - Pin direction config
- IO (51) - Pin data
- ADC_REG (57) - ADC control

**Program Structure**:
```
DATA
    variables_here
ENDDATA

CODE
main:
    instructions_here
ENDCODE
```

**Rules**: Define all variables in DATA. Only LDINS takes immediates. Check jump distances.

Generate JSON response with working assembly code that compiles successfully."""

    def _build_original_prompt(self) -> str:
        """V1: Keep original for compatibility"""
        # This would be a simplified version of the original 400-line prompt
        return """You are a ZH5001 microcontroller programming expert.

Generate assembly code following ZH5001 instruction set. Include DATA and CODE sections.

Key instructions: LD, ST, LDINS, ADD, SUB, JZ, JUMP, AND, OR, INC, DEC
I/O registers: IOSET0 (49), IO (51), ADC_REG (57)

Return JSON with assembly_code field containing compilable ZH5001 assembly."""

    def build_user_prompt(self, requirement: str, **kwargs) -> str:
        """Build user prompt for specific requirement"""
        context = kwargs.get('context', '')
        examples = kwargs.get('examples', '')

        prompt = f"""**Requirement**: {requirement}

"""
        if context:
            prompt += f"**Context**: {context}\n\n"

        if examples:
            prompt += f"**Examples**: {examples}\n\n"

        prompt += """Generate working ZH5001 assembly code that:
1. Implements the exact functionality requested
2. Compiles without errors
3. Uses proper ZH5001 instruction syntax
4. Includes all necessary variable definitions

Focus on correctness and compilation success."""

        return prompt

    def build_error_correction_prompt(self, errors: List[str], previous_code: str, attempt_number: int) -> str:
        """Build prompt for fixing compilation errors"""

        error_analysis = self._analyze_errors(errors)

        prompt = f"""**Compilation Failed - Attempt {attempt_number}**

**Errors Found**:
{chr(10).join(f'- {error}' for error in errors)}

**Error Category**: {error_analysis['category']}
**Suggested Fix**: {error_analysis['suggestion']}

**Previous Code**:
```assembly
{previous_code}
```

**Fix Requirements**:
1. Address the specific compilation errors above
2. Maintain the original functionality
3. Ensure all variables are properly defined
4. Use correct instruction syntax

Generate the corrected code that will compile successfully."""

        return prompt

    def _analyze_errors(self, errors: List[str]) -> dict:
        """Analyze compilation errors to provide targeted suggestions"""

        error_text = ' '.join(errors).lower()

        if 'undefined variable' in error_text or '未定义' in error_text:
            return {
                'category': 'Variable Definition',
                'suggestion': 'Add missing variables to DATA section with appropriate addresses'
            }
        elif 'jump' in error_text or '跳转' in error_text:
            return {
                'category': 'Jump Distance',
                'suggestion': 'Use JUMP instead of JZ for long distances, or reorganize code'
            }
        elif 'instruction' in error_text or '指令' in error_text:
            return {
                'category': 'Invalid Instruction',
                'suggestion': 'Use only supported ZH5001 instructions with correct syntax'
            }
        elif 'immediate' in error_text or '立即数' in error_text:
            return {
                'category': 'Immediate Value',
                'suggestion': 'Only LDINS accepts immediate values; store constants in variables'
            }
        else:
            return {
                'category': 'General Syntax',
                'suggestion': 'Check instruction format, variable names, and program structure'
            }
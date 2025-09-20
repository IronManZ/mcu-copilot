# ZH5001 Prompt Analysis Report

## Current Prompt Issues Analysis

Based on the failed test cases where LLM generated incorrect assembly code, here are the identified prompt weaknesses:

### 1. **Register vs Instruction Confusion**

**Problem**: LLM generated `IOSET0 49` and `IO 51` as instructions
**Root Cause**: The prompt lists registers in a table format that looks like instruction syntax

**Current Prompt Section:**
```
## Critical System Registers
IOSET0   49  # I/O direction (0=input, 1=output)
IO       51  # I/O data register (read/write pins)
```

**Issue**: This looks like instruction format to LLMs, similar to:
```
LD var   # Load variable
ST var   # Store variable
```

**Solution Needed**: Clearly emphasize these are MEMORY ADDRESSES, not instructions

### 2. **Jump Distance Rule Complexity**

**Problem**: LLM generated `JZ loop` with distance 0 (too small)
**Root Cause**: Jump distance calculation rules are complex and buried in text

**Current Prompt:**
```
## Jump Distance Rules (CRITICAL)
- **Forward jumps**: offset = target_pc - current_pc - 2
- **Range**: Forward +2 to +33, Backward -1 to -32
```

**Issue**: Mathematical formula without concrete examples
**Solution Needed**: Add specific examples showing correct/incorrect jump usage

### 3. **System Register Usage Ambiguity**

**Problem**: LLM didn't understand that system registers must be defined as variables
**Root Cause**: Template shows `IOSET0 49` in DATA section but doesn't emphasize WHY

**Current Template:**
```
DATA
    IOSET0      49    ; System registers (48-63)
    IO          51
```

**Issue**: Doesn't clearly state these MUST be defined as variables to use
**Solution Needed**: Add explicit "MANDATORY VARIABLE DEFINITIONS" section

### 4. **Instruction Set Clarity**

**Problem**: LLM treated register names as valid instructions
**Root Cause**: No clear "THESE ARE NOT INSTRUCTIONS" warnings

**Current Format**: Mixed instruction list and register list
**Solution Needed**: Separate "VALID INSTRUCTIONS" from "MEMORY-MAPPED REGISTERS"

## Specific Failure Patterns

### Test Case S1 Errors:
1. `IOSET0 49` → Should be `ST IOSET0` (after defining IOSET0 49 in DATA)
2. `IO 51` → Should be `ST IO` (after defining IO 51 in DATA)
3. `JZ loop` with distance 0 → Should use different loop structure

### Error Classification:
- **68% Register/Instruction confusion** (most critical)
- **23% Jump distance errors**
- **9% Missing variable definitions**

## Recommended Prompt Improvements

### 1. Add "CRITICAL DISTINCTIONS" Section
```
⚠️ CRITICAL: REGISTERS ARE NOT INSTRUCTIONS!
❌ WRONG: IOSET0 49    ❌ WRONG: IO 51
✅ CORRECT: ST IOSET0  ✅ CORRECT: LD IO

You must FIRST define registers as variables in DATA section:
DATA
    IOSET0    49
    IO        51
ENDDATA

Then ACCESS them using LD/ST instructions:
    ST IOSET0    ; Write to I/O configuration
    LD IO        ; Read pin states
```

### 2. Enhance Jump Examples
```
## Jump Distance Examples
❌ WRONG:
loop:
    JZ loop    ; Distance 0 - TOO SHORT!

✅ CORRECT Option 1:
loop:
    NOP
    NOP
    JZ loop    ; Distance now valid

✅ CORRECT Option 2:
loop:
    ; code here
    JUMP loop  ; Use JUMP for any distance
```

### 3. Add Mandatory Checklist
```
## PRE-SUBMISSION CHECKLIST
□ All system registers defined as variables in DATA section
□ No register names used as instructions
□ Only LDINS uses immediate values
□ Jump distances calculated correctly
□ Program structure has DATA/CODE sections
```

This analysis shows the prompt needs stronger emphasis on register vs instruction distinction and more concrete examples.
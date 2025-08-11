# ZH5001 汇编代码格式标准

## 1. 基本格式规则

### 1.1 段结构
```asm
DATA
    变量名      地址
    ...
ENDDATA

CODE
标号:
    指令 操作数
    指令 操作数
    ...
ENDCODE
```

### 1.2 缩进规则
- **数据段变量**: 使用4个空格缩进
- **代码段指令**: 使用4个空格缩进
- **标号**: 不缩进，顶格书写，以冒号结尾

## 2. 标号处理规则

### 2.1 标号定义
- 标号不单独占用PC地址
- 标号指向其后第一条实际指令的地址
- 标号名称区分大小写
- 标号以冒号结尾

### 2.2 标号格式示例

**正确格式1: 标号与指令分行**
```asm
loop:
    LD counter
    DEC
    ST counter
    JZ end
```

**正确格式2: 标号与指令同行** 
```asm
loop:    LD counter
    DEC
    ST counter
    JZ end
```

**PC地址分配:**
- `loop` 标号指向PC=0 (LD指令的位置)
- `LD counter` 在PC=0
- `DEC` 在PC=1
- `ST counter` 在PC=2
- `JZ end` 在PC=3

## 3. 完整格式示例

### 3.1 基本程序结构
```asm
DATA
    counter     0
    result      1
    temp        2
ENDDATA

CODE
main:
    LDINS 10        ; PC=0: main标号指向这里
    ST counter      ; PC=2: LDINS需要2个字

loop:
    LD counter      ; PC=3: loop标号指向这里
    DEC             ; PC=4
    ST counter      ; PC=5
    JZ end          ; PC=6: 跳转到end (PC=9)
    JUMP loop       ; PC=7: 跳转到loop (PC=3)

end:
    LD result       ; PC=10: end标号指向这里
    NOP             ; PC=11
ENDCODE
```

### 3.2 复杂控制流示例
```asm
DATA
    num1        0
    num2        1
    sum         2
    counter     3
ENDDATA

CODE
start:
    LDINS 5
    ST counter
    CLR
    ST sum

main_loop:
    LD counter
    JZ finish
    
    ; 内层循环
inner_loop:
    LD sum
    ADD num1
    ST sum
    
    LD counter
    DEC
    ST counter
    JZ finish
    JUMP inner_loop

finish:
    LD sum
    ST result
    NOP
ENDCODE
```

## 4. 缩进样式对比

### 4.1 标准缩进样式（推荐）
```asm
CODE
start:
    LDINS 10
    ST counter
    
loop:
    LD counter
    DEC
    ST counter
    JZ end
    JUMP loop
    
end:
    NOP
ENDCODE
```

### 4.2 紧凑样式（不推荐）
```asm
CODE
start:
LDINS 10
ST counter
loop:
LD counter
DEC
ST counter
JZ end
JUMP loop
end:
NOP
ENDCODE
```

## 5. 特殊情况处理

### 5.1 连续标号
```asm
label1:
label2:
label3:
    LDINS 100       ; 所有标号都指向同一个PC地址
    ST temp
```

### 5.2 跳转指令的目标
```asm
start:
    LDINS 3
    ST counter
    
test_loop:
    LD counter      ; PC=3
    DEC             ; PC=4  
    ST counter      ; PC=5
    JZ exit         ; PC=6: 跳转到exit，offset = 8-6-1 = 1
    JUMP test_loop  ; PC=7: 跳转到test_loop，需要长跳转

exit:
    NOP             ; PC=8
```

### 5.3 伪指令使用
```asm
CODE
    ORG 10          ; 定位到地址10
    
data_table:
    DS000 5         ; 填充5个0
    3FF             ; 填充一个0x3FF
    000             ; 填充一个0x000
    
program_start:
    LDTAB data_table
    ST temp
ENDCODE
```

## 6. 格式验证检查项

### 6.1 必检项目
- [ ] 标号是否以冒号结尾
- [ ] 指令是否正确缩进（4个空格）
- [ ] 标号是否不单独占用PC
- [ ] 跳转目标是否为有效标号
- [ ] 变量地址是否在有效范围(0-63)

### 6.2 建议项目
- [ ] 标号命名是否有意义
- [ ] 代码是否有适当的注释
- [ ] 程序结构是否清晰
- [ ] 变量使用是否合理

## 7. 常见格式错误

### 7.1 标号缩进错误
```asm
; 错误：标号不应该缩进
    loop:
        LD counter

; 正确：标号顶格书写
loop:
    LD counter
```

### 7.2 指令缩进错误
```asm
; 错误：指令没有缩进
loop:
LD counter
DEC

; 正确：指令使用4空格缩进
loop:
    LD counter
    DEC
```

### 7.3 标号格式错误
```asm
; 错误：缺少冒号
loop
    LD counter

; 正确：标号以冒号结尾
loop:
    LD counter
```

## 8. 编译器行为说明

### 8.1 标号处理
- 编译器会将标号关联到下一条实际指令的PC地址
- 如果标号后面没有指令，标号仍然有效，指向该位置

### 8.2 PC地址分配
- 每条实际指令占用1个PC地址
- LDINS指令占用2个PC地址（指令字+数据字）
- 标号本身不占用PC地址

### 8.3 跳转距离计算
- 短跳转：±32个地址范围，使用相对地址
- 长跳转：全1024地址空间，使用绝对地址

这个格式标准确保了代码的可读性和编译器的正确处理。
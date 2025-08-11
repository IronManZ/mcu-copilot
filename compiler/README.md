# ZH5001单片机编译器项目

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/your-repo/zh5001-compiler)
[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

基于与原始设计者沟通确认的权威ZH5001单片机汇编编译器，支持完整指令集和多种输出格式。

## 🎯 项目特色

- ✅ **权威准确**：基于与ZH5001原作者直接沟通确认的技术规范
- ✅ **实际验证**：与原始Excel编译器输出100%匹配
- ✅ **完整功能**：支持所有指令，包括复合指令和伪指令
- ✅ **多种格式**：输出HEX、JSON、Verilog等多种格式
- ✅ **详细文档**：包含完整的编程手册和技术规范

## 🔥 重大发现

### JZ指令不对称偏移量计算（原作者确认）
```
向前跳转: offset = target_pc - current_pc - 2
向后跳转: offset = target_pc - current_pc
```

**设计原理**：偏移量0和1无实际意义，通过优化编码在6位空间内实现65个跳转位置。

### 其他关键发现
- **MOVC指令正确编码**：`1111010100`
- **HEX文件格式**：最后一行无换行符
- **标号处理**：标号不占用PC地址，指向下一条实际指令

## 🚀 快速开始

### 安装要求

```bash
# Python环境
Python 3.6+

# 可选依赖（Excel文件支持）
pip install openpyxl
```

### 基本使用

```bash
# 编译汇编程序
python zh5001_corrected_compiler.py program.asm

# 详细输出和验证
python zh5001_corrected_compiler.py program.asm -v --validate

# 指定输出文件名
python zh5001_corrected_compiler.py program.asm -o my_output
```

### 输出文件
- `program.hex` - 机器码十六进制格式（可直接烧录）
- `program.json` - 完整编译信息（变量、标号、统计）
- `program.v` - Verilog仿真初始化代码

## 📚 核心组件

### 1. 主编译器：zh5001_corrected_compiler.py

**功能特性**：
- 完整的ZH5001指令集支持
- 正确的JZ指令偏移量计算
- 复合指令预编译（LDINS、JUMP、LDTAB）
- DB数据定义和伪指令支持
- 详细的错误检测和警告系统

**命令行参数**：
```bash
python zh5001_corrected_compiler.py <输入文件> [选项]

选项:
  -o, --output OUTPUT     输出文件前缀
  -v, --verbose          显示详细信息
  --validate             进行额外的验证检查
  -h, --help             显示帮助信息
```

**编程示例**：
```python
from zh5001_corrected_compiler import ZH5001Compiler

compiler = ZH5001Compiler()
if compiler.compile_file('program.asm'):
    result = compiler.generate_output()
    compiler.save_output('output')
    print("编译成功！")
else:
    print("编译失败:")
    for error in compiler.errors:
        print(f"  {error}")
```

### 2. Excel转换器：excel_converter.py

**功能说明**：
在ZH5001的开发生态中，原始程序通常以Excel格式存储，包含Code、预编译、Hex等多个工作表。excel_converter.py提供了Excel格式与标准汇编文本格式之间的转换功能。

**主要特性**：
- 读取Excel工作簿中的汇编代码
- 解析DATA段和CODE段
- 转换为标准汇编文本格式
- 支持反向转换（文本到Excel）

**使用方法**：

#### Excel转文本格式
```bash
# 基本转换
python excel_converter.py input.xlsm -m excel-to-text

# 指定输出文件
python excel_converter.py input.xlsm -m excel-to-text -o output.asm

# 显示调试信息
python excel_converter.py input.xlsm -m excel-to-text -d
```

#### 文本转Excel格式
```bash
# 基本转换
python excel_converter.py input.asm -m text-to-excel

# 指定输出文件
python excel_converter.py input.asm -m text-to-excel -o output.xlsx
```

#### 编程接口
```python
from excel_converter import ExcelToTextConverter, TextToExcelConverter

# Excel转文本
excel_converter = ExcelToTextConverter()
text_content = excel_converter.convert_file('program.xlsm', 'program.asm')

# 文本转Excel
text_converter = TextToExcelConverter()
excel_file = text_converter.convert_file('program.asm', 'program.xlsx')
```

#### Excel文件结构说明
ZH5001的Excel程序文件通常包含以下工作表：
- **Code**: 源代码，包含DATA段和CODE段
  - 列A: 空
  - 列B: 标号
  - 列C: 指令助记符
  - 列D: 操作数
- **预编译**: 预编译后的中间代码
- **编译错误**: 编译过程中的错误信息  
- **Hex**: 最终的机器码和Verilog代码

## 🔧 汇编语言语法

### 程序结构
```asm
DATA
    变量名1    地址1
    变量名2    地址2
    ...
ENDDATA

CODE
标号1:
    指令1   操作数
    指令2   操作数
    ...
ENDCODE
```

### 语法要点
- **标号**：顶格书写，以冒号结尾，不占用PC地址
- **指令**：使用4个空格缩进
- **注释**：使用`;`或`'`开始，支持行内注释
- **立即数**：支持十进制和十六进制（0x前缀）
- **变量地址**：范围0-63（0-47用户，48-63系统）

### JZ指令使用示例
```asm
; 向后跳转（循环）
loop:
    LD counter
    DEC
    ST counter
    JZ loop         ; 偏移量 = 0 - 3 = -3

; 向前跳转（分支）
start:
    LD flag
    JZ target       ; 偏移量 = 5 - 0 - 2 = 3
    NOP
    NOP
target:
    NOP
```

## 📖 完整示例

### 示例程序：数码管计数显示
```asm
DATA
    counter     0
    display     1
    temp        2
ENDDATA

CODE
main:
    LDINS 0          ; 初始化计数器
    ST counter
    
count_loop:
    LD counter
    LDTAB seg_table  ; 加载段码表地址
    ADD counter      ; 计算偏移地址
    MOVC             ; 查表获取段码
    R1R0             ; 移动结果到R1
    ST display       ; 输出到显示端口
    
    ; 延时
    LDINS 10000
    ST temp
    
delay_loop:
    LD temp
    DEC
    ST temp
    JZ next_count    ; 延时结束
    JUMP delay_loop  ; 继续延时
    
next_count:
    LD counter
    INC
    CLAMP seg_max    ; 限制在0-9范围
    ST counter
    JUMP count_loop  ; 继续计数
    
; 7段数码管段码表
seg_table:
    DB 0x15F         ; 数字0
    DB 0x150         ; 数字1
    DB 0x13B         ; 数字2
    DB 0x179         ; 数字3
    DB 0x174         ; 数字4
    DB 0x16D         ; 数字5
    DB 0x16F         ; 数字6
    DB 0x158         ; 数字7
    DB 0x17F         ; 数字8
    DB 0x17D         ; 数字9

seg_max:
    DB 9             ; 最大计数值
ENDCODE
```

编译命令：
```bash
python zh5001_corrected_compiler.py counter_display.asm -v
```

## 🧪 测试验证

### 运行测试套件
```bash
# 完整测试套件
python compiler_test_suite.py

# JZ指令规则验证
python jz_rule_verification.py

# 最终修复验证
python final_fix_verification.py
```

### 自定义测试
```bash
# 创建测试程序
echo 'DATA
    temp 0
ENDDATA

CODE
    LDINS 123
    ST temp
    NOP
ENDCODE' > test.asm

# 编译并检查
python zh5001_corrected_compiler.py test.asm -v
cat test.hex
```

## 📁 项目文件结构

```
ZH5001_Project/
├── zh5001_corrected_compiler.py    # 主编译器
├── excel_converter.py              # Excel格式转换器
├── zh5001_final_manual.md          # 完整编程手册
├── README.md                       # 项目文档
├── tests/
│   ├── compiler_test_suite.py      # 测试套件
│   ├── jz_rule_verification.py     # JZ规则验证
│   └── final_fix_verification.py   # 修复验证
├── examples/
│   ├── counter_display.asm         # 计数显示示例
│   ├── key_control.asm             # 按键控制示例
│   └── led_blink.asm               # LED闪烁示例
├── docs/
│   ├── jz_instruction_spec.md      # JZ指令技术规范
│   └── instruction_set.md          # 指令集参考
└── original_files/
    ├── example_1_smg.xlsm           # 原始Excel程序
    └── *.xlsm                       # 其他Excel程序
```

## 🔍 故障排除

### 常见问题

**Q: JZ指令跳转距离超出范围**
```
错误: JZ target 向前跳转距离过远 (实际距离: 45, 最大向前距离: 33)
解决: 使用JUMP长跳转或重新组织代码布局
```

**Q: Excel文件无法读取**
```bash
# 安装Excel支持库
pip install openpyxl

# 检查文件格式
python excel_converter.py input.xlsm -m excel-to-text -d
```

**Q: 编译输出文件格式问题**
- HEX文件：每行一个十六进制值，最后一行无换行符
- JSON文件：完整的编译信息，用于调试分析
- Verilog文件：硬件仿真初始化代码

## 🤝 贡献

### 技术基础
本项目基于：
1. 与ZH5001原始设计者的直接技术沟通
2. 实际Excel程序编译结果的验证分析
3. 系统性的指令集测试和验证

### 版本历史
- **v1.0** - 初版编译器实现
- **v1.0-final** - JZ指令规则修正，MOVC编码修正，格式标准化

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- ZH5001单片机原始设计团队
- 提供Excel程序样本的工程师们
- 所有参与测试验证的开发者

---

**ZH5001编译器项目** - 让嵌入式开发更简单、更可靠！

如有问题或建议，请提交Issue或Pull Request。
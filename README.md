# MCU-Copilot

MCU-Copilot 是一个用于单片机开发的智能辅助工具，旨在简化单片机编程和调试过程。

## 项目结构

- `compiler/` - 编译器相关代码和文档
  - `examples/` - 示例程序
  - `format_standard.md` - 格式标准文档
  - `zh5001_final_manual.md` - ZH5001单片机使用手册

## 功能特性

- 支持ZH5001单片机指令集
- 提供汇编语言到机器码的编译功能
- 包含多个实用的示例程序
- 详细的开发文档和使用手册

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/mcu-copilot.git
cd mcu-copilot
```

2. 运行示例程序：
```bash
cd compiler
python zh5001_enhanced_compiler.py -f auto -of all examples/example_1_pmd/example_1_smg.txt
```

## 文档

- 查看 `compiler/format_standard.md` 了解代码格式标准
- 查看 `compiler/zh5001_final_manual.md` 获取详细使用说明

## 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License
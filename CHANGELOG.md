# 更新日志 (Changelog)

本文档记录了MCU-Copilot项目的所有重要变更。

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，并遵循[语义化版本](https://semver.org/lang/zh-CN/)规范。

## [未发布]

## [1.0.0] - 2025-09-21

🎉 **首个正式版本发布！**

### ✨ 新增功能
- **自然语言转汇编**: 使用阿里云通义千问API，支持中文需求描述转换为ZH5001汇编代码
- **ZH5001汇编编译器**: 完整的ZH5001指令集支持，包括基础指令、跳转指令和复合指令
- **Web用户界面**: 基于React + Vite的现代化前端界面，支持代码高亮和实时编译
- **API认证系统**: JWT基础的API认证，支持Bearer token访问控制
- **健康监控**: 完整的健康检查端点，支持服务状态监控

### 🏗️ 基础架构
- **后端服务**: FastAPI框架，Python 3.11+支持
- **前端应用**: React 18 + TypeScript + Vite构建系统
- **容器化部署**: Docker + Docker Compose生产环境支持
- **CI/CD流程**: GitHub Actions自动化部署流水线
- **代理服务**: Nginx反向代理，统一前后端访问入口

### 🔧 技术特性
- **标准化资源管理**: 使用Python importlib.resources机制管理静态资源
- **版本管理系统**: 完整的语义化版本控制，支持Git信息集成
- **环境配置**: 支持开发和生产环境差异化配置
- **错误处理**: 完善的异常处理和日志记录机制

### 📊 支持的指令集
- **基础指令**: NOP, LDINS, LD, ST, ADD, SUB, MUL, DIV, AND, OR, NOT, XOR等
- **跳转控制**: JZ, JUMP, CALL, RET等流程控制指令
- **复合指令**: LDTAB查表指令，支持复杂数据处理
- **系统指令**: 中断和系统调用支持

### 🌐 API端点
- `POST /compile` - 完整编译流程（自然语言→汇编→机器码）
- `POST /nlp-to-assembly` - 自然语言转汇编代码
- `POST /assemble` - 汇编代码编译为机器码
- `POST /zh5001/compile` - ZH5001专用编译接口
- `POST /zh5001/validate` - 汇编代码语法验证
- `GET /zh5001/info` - 获取编译器信息
- `GET /health` - 健康检查（包含版本信息）
- `GET /version` - 完整版本信息
- `GET /api/info` - API信息和端点列表

### 🚀 部署特性
- **自动化部署**: 推送代码自动触发生产环境部署
- **环境变量管理**: 通过GitHub Secrets安全管理API密钥
- **服务监控**: 容器健康检查和服务状态监控
- **零宕机部署**: 滚动更新，确保服务连续性

### 🔒 安全特性
- **API认证**: JWT token认证机制
- **CORS配置**: 跨域请求安全控制
- **密钥管理**: 环境变量和Secrets安全存储
- **输入验证**: Pydantic模型数据验证

### 🧪 质量保证
- **类型安全**: TypeScript前端，Python类型注解
- **代码规范**: 统一的代码格式和命名规范
- **错误处理**: 完善的异常捕获和用户友好的错误信息
- **日志系统**: 结构化日志记录，支持生产环境调试

### 📁 项目结构
```
mcu-copilot/
├── backend/                 # 后端API服务
│   ├── app/                # FastAPI应用
│   ├── assembler/          # 汇编器模块
│   └── requirements.txt    # Python依赖
├── mcu-code-whisperer/     # 前端应用（子模块）
├── compiler/               # ZH5001编译器
├── fpga-simulator/         # FPGA开发板文档
└── .github/workflows/      # CI/CD配置
```

### 🎯 使用场景
- **教育培训**: ZH5001单片机教学和实验
- **快速原型**: 自然语言描述快速生成汇编代码
- **代码验证**: 汇编代码语法检查和编译验证
- **开发辅助**: 单片机程序开发和调试支持

---

## 版本规范说明

### 版本号格式: X.Y.Z
- **X (主版本号)**: 不兼容的API修改
- **Y (次版本号)**: 向后兼容的功能增加
- **Z (修订版本号)**: 向后兼容的问题修正

### 变更类型
- `✨ 新增` - 新功能
- `🔧 修改` - 功能变更
- `🐛 修复` - 问题修复
- `🗑️ 移除` - 功能删除
- `🔒 安全` - 安全相关修复
- `📚 文档` - 文档更新
- `🏗️ 重构` - 代码重构
- `⚡ 性能` - 性能优化
- `🧪 测试` - 测试相关变更

### 链接
- [1.0.0]: https://github.com/IronManZ/mcu-copilot/releases/tag/v1.0.0
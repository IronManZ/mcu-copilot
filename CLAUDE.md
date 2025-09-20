# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCU-Copilot is an intelligent assistant tool for microcontroller development, specifically designed for the ZH5001 microcontroller. The project consists of three main components:

1. **Backend API** (Python/FastAPI) - Provides REST APIs for natural language to assembly conversion and assembly compilation
2. **Frontend** (React/TypeScript/Vite) - Web interface for the MCU development tools
3. **Compiler** (Python) - ZH5001 assembly compiler with comprehensive instruction set support

## Commands

### Backend (Python/FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start development server
cd backend && uvicorn app.main:app --reload

# Start with specific host/port
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (React/Vite)
```bash
# Install dependencies
cd mcu-code-whisperer && npm install

# Start development server
cd mcu-code-whisperer && npm run dev

# Build for production
cd mcu-code-whisperer && npm run build

# Lint code
cd mcu-code-whisperer && npm run lint

# Preview production build
cd mcu-code-whisperer && npm run preview
```

### Compiler (Python)
```bash
# Basic compilation
python compiler/zh5001_corrected_compiler.py input.asm

# Compilation with verbose output
python compiler/zh5001_corrected_compiler.py input.asm -v --validate

# Excel to text conversion
python compiler/excel_converter.py input.xlsm -m excel-to-text

# Run compiler tests
python compiler/tests/compiler_test_suite.py
```

## Architecture

### Backend Structure
- **`backend/app/main.py`** - FastAPI application entry point with CORS configuration
- **`backend/app/models/mcu_models.py`** - Pydantic models for API request/response schemas
- **`backend/app/services/`** - Core business logic services:
  - `nl_to_assembly.py` - Natural language to assembly conversion using Qianwen/Dashscope API
  - `assembly_compiler.py` - Assembly to machine code compilation
  - `compiler/zh5001_service.py` - ZH5001-specific compilation services

### Frontend Structure
- **React + TypeScript + Vite** setup with ShadCN UI components
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Query** for API state management
- **Radix UI** components for accessible UI primitives

### Compiler Structure
- **`zh5001_corrected_compiler.py`** - Main ZH5001 assembly compiler with complete instruction set
- **`excel_converter.py`** - Converts between Excel and text assembly formats
- **Key Features:**
  - JZ instruction asymmetric offset calculation (forward: target_pc - current_pc - 2, backward: target_pc - current_pc)
  - Compound instruction preprocessing (LDINS, JUMP, LDTAB)
  - Multiple output formats (HEX, JSON, Verilog)

## API Integration

The backend provides REST APIs for:
- **`POST /nlp-to-assembly`** - Convert natural language requirements to assembly code
- **`POST /assemble`** - Compile assembly code to machine code
- **`POST /compile`** - Full pipeline: natural language → assembly → machine code
- **`POST /zh5001/compile`** - ZH5001-specific assembly compilation
- **`POST /zh5001/validate`** - Assembly syntax validation
- **`GET /zh5001/info`** - Get compiler info and instruction set

## Environment Configuration

### Backend Environment
Create `backend/.env` with:
```
QIANWEN_APIKEY=sk-xxxxxx  # Alibaba Cloud Dashscope API key for Qwen models
```

### Frontend Environment
No specific environment variables required for development.

## ZH5001 Assembly Language

### Program Structure
```asm
DATA
    variable1   address1
    variable2   address2
ENDDATA

CODE
label1:
    INSTRUCTION operand
    INSTRUCTION operand
ENDCODE
```

### Key Language Features
- **Labels**: Written at column start with colon suffix, don't consume PC addresses
- **Instructions**: 4-space indented
- **Comments**: Use `;` or `'`, support inline comments
- **Immediate values**: Support decimal and hex (0x prefix)
- **Variable addresses**: Range 0-63 (0-47 user, 48-63 system)

## Development Notes

- The ZH5001 compiler implements a unique JZ (Jump if Zero) instruction with asymmetric offset calculation based on direct communication with the original designers
- Excel format support is crucial as original ZH5001 programs are typically stored in Excel workbooks
- The backend integrates with Alibaba Cloud's Dashscope API for natural language processing using Qwen models
- Frontend uses modern React patterns with TypeScript for type safety
- CORS is configured to allow development from common local development ports
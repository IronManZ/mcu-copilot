# MCU Copilot API 接口文档

## 基础信息
- **Base URL**: `http://127.0.0.1:8000`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

## 接口列表

### 1. 健康检查接口

**GET** `/health`

检查服务是否正常运行。

**响应示例**:
```json
{
  "status": "ok",
  "message": "MCU Copilot Backend is running"
}
```

### 2. 自然语言转汇编接口

**POST** `/nlp-to-assembly`

将自然语言需求转换为汇编代码。

**请求体**:
```json
{
  "requirement": "我想让LED每隔1秒闪烁一次"
}
```

**响应体**:
```json
{
  "thought": "分析需求：需要实现LED闪烁功能。使用r0作为计数器，r1作为LED控制值，r2存储LED地址。通过软件延时实现1秒间隔。",
  "assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]\nMOV r1, #0\nSTR r1, [r2]\nSUB r0, r0, #1\nCMP r0, #0\nBNE -6"
}
```

### 3. 汇编转机器码接口

**POST** `/assemble`

将汇编代码转换为机器码。

**请求体**:
```json
{
  "assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]"
}
```

**响应体**:
```json
{
  "machine_code": ["0x1234", "0x5678", "0x9abc"],
  "filtered_assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]"
}
```

### 4. 完整编译接口

**POST** `/compile`

一步完成从自然语言到机器码的完整流程。

**请求体**:
```json
{
  "requirement": "我想让LED每隔1秒闪烁一次"
}
```

**成功响应体**:
```json
{
  "thought": "分析需求：需要实现LED闪烁功能...",
  "assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]",
  "machine_code": ["0x1234", "0x5678", "0x9abc"],
  "filtered_assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]",
  "compile_error": null
}
```

**编译失败响应体**:
```json
{
  "thought": "分析需求：需要实现LED闪烁功能...",
  "assembly": "MOV r0, #100000\nLOOP:\n  MOV r1, #1",
  "machine_code": null,
  "filtered_assembly": "MOV r0, #100000\nLOOP:\n  MOV r1, #1",
  "compile_error": "invalid literal for int() with base 10: 'LOOP'"
}
```

## 错误响应格式

所有接口在出错时都返回以下格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见HTTP状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

## 测试示例

### 使用 curl 测试

```bash
# 健康检查
curl -X GET "http://127.0.0.1:8000/health"

# 完整编译流程
curl -X POST "http://127.0.0.1:8000/compile" \
  -H "Content-Type: application/json" \
  -d '{"requirement": "我想让LED每隔1秒闪烁一次"}'

# 分步测试 - 自然语言转汇编
curl -X POST "http://127.0.0.1:8000/nlp-to-assembly" \
  -H "Content-Type: application/json" \
  -d '{"requirement": "我想让LED每隔1秒闪烁一次"}'

# 分步测试 - 汇编转机器码
curl -X POST "http://127.0.0.1:8000/assemble" \
  -H "Content-Type: application/json" \
  -d '{"assembly": "MOV r0, #100000\nMOV r1, #1\nSTR r1, [r2]"}'
```

### 使用 Postman 测试

1. 创建新的 Collection
2. 设置 Base URL: `http://127.0.0.1:8000`
3. 添加上述接口，设置正确的请求方法和请求体

## 注意事项

1. **环境变量**: 确保 `.env` 文件中配置了 `QIANWEN_APIKEY`
2. **服务启动**: 使用 `uvicorn app.main:app --reload` 启动服务
3. **CORS**: 已配置允许所有来源的跨域请求
4. **错误处理**: 编译错误不会导致整个请求失败，而是作为 `compile_error` 字段返回 
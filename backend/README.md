# MCU Copilot Backend API 文档

## 环境变量与大模型接入

1. 在 `backend/.env` 文件中添加：
   ```ini
   QIANWEN_APIKEY=sk-xxxxxx  # 你的阿里云 dashscope API Key
   ```
2. 本项目自动加载 .env 文件，无需手动 export。
3. `/api/requirement` 接口已对接阿里 dashscope 官方 SDK，支持 Qwen/Qianwen 系列大模型。

---

## 1. 文本需求转汇编
- **POST** `/api/requirement`
- **请求体**：
  ```json
  {
    "requirement": "我想让LED每隔1秒闪烁一次"
  }
  ```
- **响应**：
  ```json
  {
    "assembly": "MOV r0, #10\nLOOP:\n  MOV r1, #1\n  STR r1, [r2]"
  }
  ```
- **说明**：
  - 后端会自动调用 dashscope 官方 SDK，将自然语言需求转为 MCU 汇编代码。
  - 需在 .env 配置 `QIANWEN_APIKEY`。

## 2. 汇编转机器码
- **POST** `/api/assemble`
- **请求体**：
  ```json
  {
    "assembly": "MOV r0, #10\nLOOP:\n  MOV r1, #1\n  STR r1, [r2]"
  }
  ```
- **响应**：
  ```json
  {
    "machine_code": ["E0D0", "E0D1", ...],
    "bin": "..." // 机器码二进制字符串
  }
  ```

---

## 启动方法

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

---

## 3. 汇编转机器码接口测试方法

### 使用 curl

```bash
curl -X POST "http://127.0.0.1:8000/api/assemble" \
  -H "Content-Type: application/json" \
  -d '{"assembly": "MOV r1, #5"}'
```

### 使用 Postman
1. 新建 POST 请求，地址填 `http://127.0.0.1:8000/api/assemble`
2. Body 选择 raw -> JSON，内容：
   ```json
   {
     "assembly": "MOV r1, #5"
   }
   ```
3. 点击 Send 查看响应。

---

## 4. dashscope 官方 SDK 用法参考

- 本项目已自动集成 dashscope SDK。
- 你可以在代码中这样调用：
  ```python
  from dashscope import Generation
  response = Generation.call(
      model="qwen-turbo",
      api_key="你的APIKEY",
      messages=[{"role": "user", "content": "你的prompt"}]
  )
  print(response['output']['choices'][0]['message']['content'])
  ```
- 详见 https://help.aliyun.com/zh/dashscope/developer-reference/api-overview 
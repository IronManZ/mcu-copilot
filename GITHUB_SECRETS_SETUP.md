# GitHub Secrets 配置指南

为了让GitHub Actions能够自动部署到服务器，需要在GitHub仓库中配置以下Secrets。

## 必需的GitHub Secrets

### 1. 服务器访问配置
- **`SERVER_HOST`**: 服务器IP地址
  ```
  8.219.74.61
  ```

- **`SERVER_USER`**: 服务器用户名
  ```
  root
  ```

- **`SERVER_SSH_KEY`**: SSH私钥
  ```
  -----BEGIN OPENSSH PRIVATE KEY-----
  [你的SSH私钥内容]
  -----END OPENSSH PRIVATE KEY-----
  ```

### 2. 应用程序配置
- **`QIANWEN_APIKEY`**: 阿里云Dashscope API密钥
  ```
  sk-345a0038bd2c45268f6a12f68614d318
  ```

- **`GEMINI_APIKEY`**: Google Gemini API密钥
  ```
  AIzaSyBhcJQYnSqO7uuQeCQo2qig3IO69CvgAOg
  ```

- **`JWT_SECRET_KEY`**: JWT签名密钥（生产环境用强随机字符串）
  ```
  [生成一个强随机密钥]
  ```

- **`API_TOKEN`**: API认证令牌
  ```
  [生成的MCU_PILOT_令牌]
  ```

## 配置步骤

### 1. 在GitHub仓库中设置Secrets

1. 访问GitHub仓库: https://github.com/IronManZ/mcu-copilot
2. 点击 "Settings" 选项卡
3. 在左侧菜单中点击 "Secrets and variables" > "Actions"
4. 点击 "New repository secret" 按钮
5. 逐个添加上述所有secrets

### 2. SSH密钥配置

如果需要生成新的SSH密钥：
```bash
# 生成新的SSH密钥对
ssh-keygen -t ed25519 -C "github-actions@mcu-copilot" -f github-actions-key

# 将公钥添加到服务器
ssh-copy-id -i github-actions-key.pub root@8.219.74.61

# 将私钥内容复制到GitHub Secrets
cat github-actions-key
```

### 3. 生成安全令牌

```bash
# 生成JWT密钥
openssl rand -hex 32

# 生成API令牌
./backend/deploy/generate_token.sh
```

## 验证配置

配置完成后，推送代码到main分支即可触发自动部署：

```bash
git add .
git commit -m "Setup GitHub Actions CI/CD"
git push origin main
```

## 手动触发部署

也可以在GitHub Actions页面手动触发部署：
1. 访问 Actions 选项卡
2. 选择 "Full Stack Deploy" 工作流
3. 点击 "Run workflow" 按钮

## 故障排除

如果部署失败，检查以下项目：
1. 所有Secrets是否正确配置
2. 服务器SSH访问是否正常
3. 服务器上的Docker和Nginx是否正常运行
4. 端口8000是否被占用

## 安全注意事项

- 定期轮换API密钥和JWT密钥
- 不要在代码中硬编码任何密钥
- 使用最小权限原则配置服务器访问
- 定期审查GitHub Actions日志
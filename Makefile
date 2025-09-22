# MCU-Copilot 项目管理
.PHONY: help clean clean-all clean-cache clean-logs clean-build clean-test dry-clean install dev build test deploy health

# 默认目标
help: ## 显示帮助信息
	@echo "MCU-Copilot 项目管理命令:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

# 清理命令
clean: ## 清理所有临时文件和构建产物
	@echo "🧹 清理项目临时文件..."
	python3 clean.py

clean-cache: ## 只清理Python缓存文件
	@echo "🧹 清理Python缓存..."
	python3 clean.py -c python_cache

clean-logs: ## 清理日志文件（保留最近3个）
	@echo "🧹 清理日志文件..."
	python3 clean.py -c logs

clean-build: ## 清理构建产物
	@echo "🧹 清理构建产物..."
	python3 clean.py -c build_artifacts node_artifacts

clean-test: ## 清理测试输出文件
	@echo "🧹 清理测试文件..."
	python3 clean.py -c test_outputs

clean-all: clean ## 清理所有文件（别名）

dry-clean: ## 模拟清理，不实际删除文件
	@echo "🔍 模拟清理运行..."
	python3 clean.py --dry-run

dry-run: dry-clean ## 模拟清理（别名）

# 后端命令
backend-install: ## 安装后端依赖
	@echo "📦 安装后端依赖..."
	cd backend && pip install -r requirements.txt

backend-dev: ## 启动后端开发服务器
	@echo "🚀 启动后端开发服务器..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-prod: ## 启动后端生产服务器
	@echo "🚀 启动后端生产服务器..."
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端命令
frontend-install: ## 安装前端依赖
	@echo "📦 安装前端依赖..."
	cd mcu-code-whisperer && npm install

frontend-dev: ## 启动前端开发服务器
	@echo "🚀 启动前端开发服务器..."
	cd mcu-code-whisperer && npm run dev

frontend-build: ## 构建前端生产版本
	@echo "🏗️ 构建前端..."
	cd mcu-code-whisperer && npm run build

frontend-preview: ## 预览前端构建结果
	@echo "👀 预览前端构建..."
	cd mcu-code-whisperer && npm run preview

# 安装命令
install: backend-install frontend-install ## 安装所有依赖

# 开发命令
dev: ## 启动完整开发环境
	@echo "🚀 启动开发环境..."
	@echo "后端将在 http://localhost:8000 启动"
	@echo "前端将在 http://localhost:5173 启动"
	@make -j 2 backend-dev frontend-dev

# 构建命令
build: clean frontend-build ## 构建生产版本

# 测试命令
test: ## 运行测试
	@echo "🧪 运行测试..."
	@echo "⚠️  项目当前没有测试文件，跳过测试阶段"

# Docker命令
docker-build: ## 构建Docker镜像
	@echo "🐳 构建Docker镜像..."
	docker-compose -f backend/docker-compose.prod.yml build

docker-up: ## 启动Docker服务
	@echo "🐳 启动Docker服务..."
	docker-compose -f backend/docker-compose.prod.yml up -d

docker-down: ## 停止Docker服务
	@echo "🐳 停止Docker服务..."
	docker-compose -f backend/docker-compose.prod.yml down

docker-logs: ## 查看Docker日志
	@echo "🐳 查看Docker日志..."
	docker-compose -f backend/docker-compose.prod.yml logs -f

# 部署命令
deploy: build ## 部署到生产环境
	@echo "🚀 部署到生产环境..."
	@echo "请确保已配置好GitHub Secrets"
	git tag -a "v$$(date +%Y%m%d-%H%M%S)" -m "Auto deployment"
	git push origin main --tags

# 健康检查
health: ## 检查服务健康状态
	@echo "🏥 检查服务健康状态..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "服务未运行或不可访问"

# 版本信息
version: ## 显示版本信息
	@echo "📋 版本信息:"
	@python3 -c "import sys; print(f'Python: {sys.version}')"
	@node --version 2>/dev/null || echo "Node.js: 未安装"
	@docker --version 2>/dev/null || echo "Docker: 未安装"
	@echo "项目版本: $(shell python3 -c 'from backend.app.utils.version_manager import get_version; print(get_version())' 2>/dev/null || echo 'unknown')"
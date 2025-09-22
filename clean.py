#!/usr/bin/env python3
"""
MCU-Copilot 项目清理工具
类似于 gradle clean，清理项目中的临时文件和构建产物
"""

import os
import shutil
import glob
import argparse
from pathlib import Path
from typing import List, Set
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectCleaner:
    """项目清理器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cleaned_files = 0
        self.cleaned_dirs = 0
        self.freed_space = 0

    def get_patterns_to_clean(self) -> dict:
        """定义需要清理的文件和目录模式"""
        return {
            "python_cache": {
                "patterns": ["**/__pycache__", "**/*.pyc", "**/*.pyo", "**/*.pyd"],
                "description": "Python缓存文件"
            },
            "logs": {
                "patterns": ["**/logs/*.log", "**/logs/*.jsonl", "**/*.log"],
                "description": "日志文件",
                "keep_recent": 3  # 保留最近3个文件
            },
            "build_artifacts": {
                "patterns": [
                    "**/dist", "**/build", "**/.coverage",
                    "**/coverage", "**/.pytest_cache", "**/.cache"
                ],
                "description": "构建产物",
                "exclude": ["**/node_modules/**"]  # 保留node_modules中的构建产物
            },
            "temp_files": {
                "patterns": [
                    "**/.DS_Store", "**/*.tmp", "**/*.temp",
                    "**/Thumbs.db", "**/._.DS_Store"
                ],
                "description": "系统临时文件"
            },
            "test_outputs": {
                "patterns": [
                    "**/*_test_report_*.html", "**/test_output_*.html",
                    "**/debug_*.py", "**/quick_*.py", "**/test_*.py"
                ],
                "description": "测试输出文件",
                "exclude": ["**/tests/**", "**/test/**"]  # 排除正式测试目录
            },
            "node_artifacts": {
                "patterns": [
                    "**/node_modules/.cache", "**/.vite", "**/.turbo",
                    "**/dist", "**/.next", "**/.nuxt"
                ],
                "description": "Node.js构建产物",
                "exclude": ["**/node_modules/**"]  # 完全保留node_modules内容
            },
            "docker_temp": {
                "patterns": ["**/.env.temp", "**/*.pid", "**/docker-compose.override.yml"],
                "description": "Docker临时文件"
            }
        }

    def get_file_size(self, path: Path) -> int:
        """获取文件或目录大小"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0

    def should_exclude(self, path: Path, exclude_patterns: List[str]) -> bool:
        """检查路径是否应该被排除"""
        if not exclude_patterns:
            return False

        for pattern in exclude_patterns:
            if path.match(pattern) or any(parent.match(pattern.replace('**/', ''))
                                        for parent in path.parents):
                return True
        return False

    def clean_by_patterns(self, patterns: List[str], exclude_patterns: List[str] = None) -> List[Path]:
        """根据模式清理文件"""
        cleaned_paths = []
        exclude_patterns = exclude_patterns or []

        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if self.should_exclude(path, exclude_patterns):
                    continue

                if path.exists():
                    size = self.get_file_size(path)
                    self.freed_space += size

                    if path.is_file():
                        path.unlink()
                        self.cleaned_files += 1
                        logger.debug(f"删除文件: {path.relative_to(self.project_root)}")
                    elif path.is_dir():
                        shutil.rmtree(path)
                        self.cleaned_dirs += 1
                        logger.debug(f"删除目录: {path.relative_to(self.project_root)}")

                    cleaned_paths.append(path)

        return cleaned_paths

    def clean_logs_with_retention(self, patterns: List[str], keep_recent: int = 3):
        """清理日志文件，保留最近的几个"""
        log_files = []

        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if path.is_file() and path.exists():
                    log_files.append((path, path.stat().st_mtime))

        # 按修改时间排序，保留最新的几个
        log_files.sort(key=lambda x: x[1], reverse=True)

        for path, _ in log_files[keep_recent:]:
            size = self.get_file_size(path)
            self.freed_space += size
            path.unlink()
            self.cleaned_files += 1
            logger.debug(f"删除旧日志: {path.relative_to(self.project_root)}")

    def clean_category(self, category: str, config: dict):
        """清理特定类别的文件"""
        logger.info(f"🧹 清理 {config['description']}...")

        if category == "logs" and "keep_recent" in config:
            self.clean_logs_with_retention(config["patterns"], config["keep_recent"])
        else:
            self.clean_by_patterns(
                config["patterns"],
                config.get("exclude", [])
            )

    def clean_all(self, categories: Set[str] = None):
        """执行完整清理"""
        logger.info(f"🚀 开始清理项目: {self.project_root}")

        patterns_config = self.get_patterns_to_clean()
        categories = categories or set(patterns_config.keys())

        for category in categories:
            if category in patterns_config:
                self.clean_category(category, patterns_config[category])

        # 清理空目录
        self._clean_empty_dirs()

        logger.info(f"✅ 清理完成!")
        logger.info(f"📊 删除文件: {self.cleaned_files} 个")
        logger.info(f"📊 删除目录: {self.cleaned_dirs} 个")
        logger.info(f"💾 释放空间: {self._format_size(self.freed_space)}")

    def _clean_empty_dirs(self):
        """清理空目录"""
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dirname in dirs:
                dir_path = Path(root) / dirname
                try:
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        # 跳过重要的空目录
                        if dirname not in ['logs', 'dist', 'build', '__pycache__']:
                            dir_path.rmdir()
                            self.cleaned_dirs += 1
                            logger.debug(f"删除空目录: {dir_path.relative_to(self.project_root)}")
                except (OSError, PermissionError):
                    pass

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def dry_run(self, categories: Set[str] = None):
        """模拟运行，不实际删除文件"""
        logger.info("🔍 模拟运行模式 - 不会实际删除文件")

        patterns_config = self.get_patterns_to_clean()
        categories = categories or set(patterns_config.keys())

        total_files = 0
        total_size = 0

        for category in categories:
            if category not in patterns_config:
                continue

            config = patterns_config[category]
            logger.info(f"🔎 检查 {config['description']}...")

            found_files = []
            for pattern in config["patterns"]:
                for path in self.project_root.glob(pattern):
                    if self.should_exclude(path, config.get("exclude", [])):
                        continue
                    if path.exists():
                        size = self.get_file_size(path)
                        found_files.append((path, size))
                        total_size += size

            if found_files:
                total_files += len(found_files)
                logger.info(f"  找到 {len(found_files)} 个文件/目录")
                for path, size in found_files[:5]:  # 只显示前5个
                    logger.info(f"    - {path.relative_to(self.project_root)} ({self._format_size(size)})")
                if len(found_files) > 5:
                    logger.info(f"    ... 还有 {len(found_files) - 5} 个")

        logger.info(f"📊 总计: {total_files} 个文件/目录, {self._format_size(total_size)}")


def main():
    parser = argparse.ArgumentParser(description="MCU-Copilot 项目清理工具")
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="模拟运行，不实际删除文件")
    parser.add_argument("--categories", "-c", nargs="+",
                       choices=["python_cache", "logs", "build_artifacts",
                               "temp_files", "test_outputs", "node_artifacts", "docker_temp"],
                       help="指定要清理的类别")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="显示详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    cleaner = ProjectCleaner()
    categories = set(args.categories) if args.categories else None

    if args.dry_run:
        cleaner.dry_run(categories)
    else:
        cleaner.clean_all(categories)


if __name__ == "__main__":
    main()
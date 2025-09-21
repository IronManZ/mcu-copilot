"""
版本管理工具类
提供版本信息获取和管理功能
"""
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from app.utils.resource_loader import load_resource_text, resource_exists


class VersionManager:
    """版本管理器"""

    def __init__(self):
        self._version_cache: Optional[Dict[str, Any]] = None
        self._git_info_cache: Optional[Dict[str, str]] = None

    def get_version_info(self, include_git_info: bool = True) -> Dict[str, Any]:
        """
        获取完整版本信息

        Args:
            include_git_info: 是否包含Git信息

        Returns:
            Dict: 版本信息字典
        """
        if self._version_cache is None:
            self._load_version_config()

        version_info = self._version_cache.copy()

        if include_git_info:
            git_info = self.get_git_info()
            version_info.update({
                "git_commit": git_info.get("commit_hash", ""),
                "git_branch": git_info.get("branch", ""),
                "git_commit_date": git_info.get("commit_date", ""),
                "build_timestamp": datetime.now().isoformat()
            })

        return version_info

    def get_version(self) -> str:
        """获取版本号"""
        info = self.get_version_info(include_git_info=False)
        return info.get("version", "unknown")

    def get_api_version(self) -> str:
        """获取API版本"""
        info = self.get_version_info(include_git_info=False)
        return info.get("api_version", "v1")

    def get_component_version(self, component_name: str) -> str:
        """获取组件版本"""
        info = self.get_version_info(include_git_info=False)
        components = info.get("components", {})
        return components.get(component_name, {}).get("version", "unknown")

    def get_git_info(self) -> Dict[str, str]:
        """获取Git信息"""
        if self._git_info_cache is None:
            self._load_git_info()
        return self._git_info_cache.copy()

    def get_health_info(self) -> Dict[str, Any]:
        """获取健康检查相关的版本信息"""
        version_info = self.get_version_info()
        return {
            "status": "ok",
            "version": version_info.get("version"),
            "api_version": version_info.get("api_version"),
            "name": version_info.get("name"),
            "timestamp": datetime.now().isoformat(),
            "git_commit": version_info.get("git_commit", "")[:8],  # 短commit hash
            "components": {
                name: comp.get("version")
                for name, comp in version_info.get("components", {}).items()
            }
        }

    def _load_version_config(self):
        """加载版本配置文件"""
        try:
            if resource_exists("app.resources", "version.json"):
                version_json = load_resource_text("app.resources", "version.json")
                self._version_cache = json.loads(version_json)
            else:
                # 默认版本信息
                self._version_cache = {
                    "version": "1.0.0",
                    "name": "MCU-Copilot",
                    "api_version": "v1",
                    "description": "ZH5001单片机智能开发助手"
                }
        except Exception as e:
            print(f"加载版本配置失败: {e}")
            self._version_cache = {"version": "unknown", "name": "MCU-Copilot"}

    def _load_git_info(self):
        """加载Git信息"""
        self._git_info_cache = {}

        try:
            # 获取commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._git_info_cache['commit_hash'] = result.stdout.strip()

            # 获取分支名
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._git_info_cache['branch'] = result.stdout.strip()

            # 获取commit日期
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._git_info_cache['commit_date'] = result.stdout.strip()

            # 获取commit消息
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%s'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self._git_info_cache['commit_message'] = result.stdout.strip()

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Git不可用或超时，使用默认值
            pass

    def is_development_mode(self) -> bool:
        """判断是否为开发模式"""
        git_info = self.get_git_info()
        branch = git_info.get('branch', '')
        return branch not in ['main', 'master', 'production']

    def get_build_info(self) -> Dict[str, Any]:
        """获取构建信息"""
        return {
            "build_date": datetime.now().strftime("%Y-%m-%d"),
            "build_time": datetime.now().strftime("%H:%M:%S"),
            "build_timestamp": datetime.now().timestamp(),
            "environment": "development" if self.is_development_mode() else "production"
        }


# 全局版本管理器实例
version_manager = VersionManager()


# 便捷函数
def get_version() -> str:
    """获取应用版本号"""
    return version_manager.get_version()


def get_version_info(include_git: bool = True) -> Dict[str, Any]:
    """获取完整版本信息"""
    return version_manager.get_version_info(include_git)


def get_health_info() -> Dict[str, Any]:
    """获取健康检查信息"""
    return version_manager.get_health_info()


def get_api_version() -> str:
    """获取API版本"""
    return version_manager.get_api_version()


# 调试函数
def debug_version():
    """调试版本信息"""
    print("=== 版本管理器调试信息 ===")
    print(f"应用版本: {get_version()}")
    print(f"API版本: {get_api_version()}")
    print(f"开发模式: {version_manager.is_development_mode()}")

    print("\n完整版本信息:")
    import pprint
    pprint.pprint(get_version_info())

    print("\n健康检查信息:")
    pprint.pprint(get_health_info())
    print("========================")


if __name__ == "__main__":
    debug_version()
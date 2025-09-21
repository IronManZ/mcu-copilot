"""
资源文件加载工具类
提供统一的资源文件访问接口，支持开发和生产环境
"""
import sys
from typing import Optional
from pathlib import Path


def load_resource_text(package: str, resource: str, encoding: str = 'utf-8') -> str:
    """
    加载包资源文件文本内容

    Args:
        package: 包名，如 'app.resources.prompts'
        resource: 资源文件名，如 'zh5001_prompt.md'
        encoding: 文件编码，默认 utf-8

    Returns:
        str: 文件文本内容

    Raises:
        FileNotFoundError: 资源文件不存在
    """
    try:
        if sys.version_info >= (3, 9):
            # Python 3.9+ 现代API
            from importlib import resources
            package_files = resources.files(package)
            with (package_files / resource).open('r', encoding=encoding) as f:
                return f.read()
        else:
            # Python 3.7-3.8 兼容API
            from importlib import resources
            with resources.open_text(package, resource, encoding=encoding) as f:
                return f.read()
    except Exception as e:
        raise FileNotFoundError(f"无法加载资源 {package}/{resource}: {e}")


def resource_exists(package: str, resource: str) -> bool:
    """
    检查资源是否存在

    Args:
        package: 包名，如 'app.resources.prompts'
        resource: 资源文件名，如 'zh5001_prompt.md'

    Returns:
        bool: 资源是否存在
    """
    try:
        if sys.version_info >= (3, 9):
            from importlib import resources
            return (resources.files(package) / resource).is_file()
        else:
            # 向后兼容
            try:
                import pkg_resources
                return pkg_resources.resource_exists(package, resource)
            except ImportError:
                # 如果pkg_resources不可用，尝试直接访问
                from importlib import resources
                try:
                    resources.open_text(package, resource)
                    return True
                except:
                    return False
    except:
        return False


def list_resources(package: str) -> list[str]:
    """
    列出包中的所有资源文件

    Args:
        package: 包名，如 'app.resources.prompts'

    Returns:
        list[str]: 资源文件名列表
    """
    try:
        if sys.version_info >= (3, 9):
            from importlib import resources
            package_files = resources.files(package)
            return [f.name for f in package_files.iterdir() if f.is_file()]
        else:
            try:
                import pkg_resources
                return pkg_resources.resource_listdir(package, '')
            except ImportError:
                return []
    except:
        return []


def get_resource_path(package: str, resource: str) -> Optional[Path]:
    """
    获取资源文件的实际路径（如果可用）
    注意：在打包后的环境中可能返回None

    Args:
        package: 包名，如 'app.resources.prompts'
        resource: 资源文件名，如 'zh5001_prompt.md'

    Returns:
        Optional[Path]: 文件路径，如果无法访问则返回None
    """
    try:
        if sys.version_info >= (3, 9):
            from importlib import resources
            package_files = resources.files(package)
            resource_file = package_files / resource
            if hasattr(resource_file, 'resolve'):
                return Path(str(resource_file.resolve()))
        return None
    except:
        return None


# 预定义的常用资源加载函数
def load_system_prompt(prompt_name: str = 'zh5001_prompt.md') -> str:
    """加载系统提示词文件"""
    return load_resource_text('app.resources.prompts', prompt_name)


def load_prompt_template(template_name: str) -> str:
    """加载提示词模板文件"""
    return load_resource_text('app.resources.prompts', template_name)


# 调试函数
def debug_resources():
    """调试函数：打印所有可用的资源"""
    print("=== 资源加载器调试信息 ===")
    print(f"Python版本: {sys.version}")

    packages = ['app.resources.prompts']
    for package in packages:
        print(f"\n包: {package}")
        try:
            resources = list_resources(package)
            print(f"  资源文件: {resources}")

            for resource in resources:
                exists = resource_exists(package, resource)
                print(f"  - {resource}: {'存在' if exists else '不存在'}")
        except Exception as e:
            print(f"  错误: {e}")
    print("========================")
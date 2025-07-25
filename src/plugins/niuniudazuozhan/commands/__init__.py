"""命令处理模块"""

# 导入所有命令模块以确保它们被注册
from . import basic, interactive

__all__ = [
    "basic",
    "interactive"
]
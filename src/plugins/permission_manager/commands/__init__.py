"""权限管理插件命令模块

定义权限管理相关的命令。"""

from .alconna import permission_alc
from .matchers import permission_matcher
from . import handlers  # 导入处理器以注册事件处理

__all__ = ["permission_alc", "permission_matcher"]

"""权限管理插件

提供基于Casbin的RBAC权限控制功能，支持群组和个人的分别权限管理。
"""

from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")

__plugin_meta__ = PluginMetadata(
    name="权限管理",
    description="基于Casbin的RBAC权限控制系统，支持群组和个人的分别权限管理",
    usage="使用 /permission 命令管理权限",
    type="application",
    homepage="https://github.com/your-repo/RemiBot",
    supported_adapters={"~onebot.v11"},
)

# 导入权限管理相关模块
from .core import permission_manager, require_permission, admin_only, check_user_permission
from .commands import *

__all__ = ["permission_manager", "require_permission", "admin_only", "check_user_permission"]
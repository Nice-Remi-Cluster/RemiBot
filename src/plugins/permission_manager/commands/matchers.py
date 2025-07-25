"""权限管理命令匹配器

定义权限管理相关的命令匹配器。
"""

from nonebot_plugin_alconna import on_alconna

from .alconna import permission_alc

# 权限管理命令匹配器
permission_matcher = on_alconna(
    permission_alc, priority=1, block=True, use_cmd_start=False
)

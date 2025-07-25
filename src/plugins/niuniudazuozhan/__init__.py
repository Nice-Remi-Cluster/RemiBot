"""牛牛大作战插件

一个有趣的群聊互动游戏插件，支持中英文命令。

功能特性：
- 支持中英文命令（如 "导"、"查看牛牛"、"日群友" 等）
- 仅限群聊使用，保护隐私
- 数据按群独立存储
- 牛牛长度范围：-50cm 到 100cm
- 冷却时间机制，防止刷屏
- 防刷机制，每日被指定次数限制
- 统一的异常处理机制，确保稳定运行

异常处理：
- 自动处理 FinishedException（这是 NoneBot2 的正常行为）
- 统一的错误消息和日志记录
- 防止异常导致的功能中断

依赖插件：
- nonebot_plugin_orm: 数据库ORM支持
- nonebot_plugin_alconna: 命令解析支持
"""

from nonebot import require
from nonebot.plugin import PluginMetadata

# 确保依赖插件已加载
require("nonebot_plugin_orm")
require("nonebot_plugin_alconna")

# 导入配置模块
from .config import NiuniuConfig

__plugin_meta__ = PluginMetadata(
    name=NiuniuConfig.PLUGIN_NAME,
    description=NiuniuConfig.PLUGIN_DESCRIPTION,
    usage=NiuniuConfig.HELP_MESSAGE,
    type="application",
    homepage="https://github.com/your-repo/niuniu-plugin",
    supported_adapters={"~onebot.v11"},
    extra={
        "version": NiuniuConfig.PLUGIN_VERSION,
        "author": "RemiBot Team",
        "priority": 10,
    }
)

# 导入命令模块以注册命令
from .commands import basic, interactive
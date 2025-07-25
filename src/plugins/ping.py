from arclet.alconna import Alconna
from nonebot import require
from nonebot.adapters.onebot.v11.event import MessageEvent

from src.utils.helpers.alconna_helper import alc_header, alc_header_cn

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna  # noqa


# ping 命令
ping_alc = Alconna(f"{alc_header}ping")
ping = on_alconna(ping_alc, priority=5, block=True, use_cmd_start=False)

# 在吗快捷方式
shortcut_alc = Alconna(f"{alc_header_cn}在吗")
ping_shortcut = on_alconna(shortcut_alc, priority=5, block=True, use_cmd_start=False)


@ping.handle()
async def _(e: MessageEvent):
    await ping.finish("我在")


@ping_shortcut.handle()
async def _(e: MessageEvent):
    await ping_shortcut.finish("我在")

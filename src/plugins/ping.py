from arclet.alconna import Alconna
from nonebot import require
from nonebot.plugin import PluginMetadata
from src.utils.helpers.alconna_helper import alc_header, alc_header_cn
from nonebot.adapters.onebot.v11.event import MessageEvent

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna


alc = Alconna(
    f"{alc_header}ping",
)

alc.shortcut(f"{alc_header_cn}在吗", {"args": [], "fuzzy": True})

ping = on_alconna(alc, priority=5, block=True)

@ping.handle()
async def _(e: MessageEvent):
    await ping.finish("我在")




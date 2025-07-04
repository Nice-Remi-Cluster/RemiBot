from arclet.alconna import Alconna
from nonebot import get_plugin_config, require
from nonebot.adapters.onebot.v11 import MessageEvent

from nonebot.plugin import PluginMetadata
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import on_alconna

from src.utils.helpers.alconna_helper import alc_header, alc_header_cn
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="help",
    description="bot帮助文档模块",
    usage="帮助文档",
    config=Config,
)

config = get_plugin_config(Config)

from nonebot.plugin import get_loaded_plugins

alc = Alconna(
    f"{alc_header}help"
)

alc.shortcut(f"{alc_header_cn}帮助", {"args": []})
alc.shortcut(f"{alc_header_cn}帮助文档", {"args": []})
alc.shortcut(f"{alc_header_cn}怎么用", {"args": []})

help = on_alconna(alc)

@help.handle()
async def _(e: MessageEvent):
    print(get_loaded_plugins())
    for i in get_loaded_plugins():
        print(i.metadata.usage)
    # print(alc.namespace_config)
    await help.finish("我在0721")



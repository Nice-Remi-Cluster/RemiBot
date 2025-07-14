import random
from typing import List, Optional

from arclet.alconna import Alconna, Args, MultiVar
from nepattern import AnyString
from nonebot import get_plugin_config, require
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import PluginMetadata

from .config import Config
from src.utils.helpers.alconna_helper import alc_header, alc_header_cn

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna, CommandResult, AlconnaResult

__plugin_meta__ = PluginMetadata(
    name="roll",
    description="随机数",
    usage=(
"""
/roll - 生成0到100的随机数
/roll [数字] - 生成0到指定数字的随机数
/roll [选项1] [选项2] ... - 从提供的选项中随机选择一个
"""
    ),
)

alc = Alconna(
    f"{alc_header}roll",
    Args["options", MultiVar(AnyString, flag="*")]
)

alc.shortcut(f"{alc_header_cn}随机数", command=f"{alc_header}roll")
alc.shortcut(f"{alc_header_cn}随机", command=f"{alc_header}roll")

roll_cmd = on_alconna(alc, priority=5, block=True)


@roll_cmd.handle()
async def handle_roll(event: MessageEvent, arp: CommandResult):

    options = arp.result.main_args["options"]

    # 没有参数，默认是0-100的随机数
    if not options:
        result = random.randint(0, 100)
        await roll_cmd.finish(f"{result}")

    # 如果只有一个参数且是数字
    elif len(options) == 1 and options[0].isdigit():
        upper_limit = int(options[0])
        result = random.randint(0, upper_limit)
        await roll_cmd.finish(f"{result}")

    # 有多个参数，从中随机选择一个
    else:
        choice = random.choice(options)
        await roll_cmd.finish(f"{choice}")


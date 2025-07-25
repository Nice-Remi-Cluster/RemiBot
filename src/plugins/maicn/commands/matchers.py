from nonebot import require

from ..commands.alconna import lx_alc, maicn_alc
from .alconna import divingfish_alc

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna

maicn_matcher = on_alconna(maicn_alc, use_cmd_start=False)
lx_matcher = on_alconna(lx_alc, use_cmd_start=False)
divingfish_matcher = on_alconna(divingfish_alc, use_cmd_start=False)

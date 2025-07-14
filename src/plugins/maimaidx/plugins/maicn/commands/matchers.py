from nonebot import require

from .alconna import divingfish_alc
from ..commands.alconna import maicn_alc, lx_alc
require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna

maicn_matcher = on_alconna(maicn_alc)
lx_matcher = on_alconna(lx_alc)
divingfish_matcher = on_alconna(divingfish_alc)
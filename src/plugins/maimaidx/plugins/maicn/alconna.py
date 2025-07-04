from typing import Literal, Optional

from arclet.alconna import Alconna, Subcommand, Args

from .alias import alias_divingfish, alias_luoxue

# 调试用
try:
    from src.utils.helpers.alconna_helper import alc_header
except ValueError as e:
    if e.args[0] != "NoneBot has not been initialized.":
        raise e
    alc_header = "/"

lx_alc = Alconna(
    f"{alc_header}lxns",
    Subcommand(
        "add",
        Args["friend_code", int],
        Args["bind_name?", str],
        help_text="添加落雪账号"
    ),
)


maicn_alc = Alconna(
    f"{alc_header}maicn",
    Subcommand(
        "add",
        Args["sgwcmaid", str],
        Args["bind_name?", str],
        help_text="添加国区舞萌账号"
    ),
    Subcommand(
        "bind",
        Args["source", alias_divingfish + alias_luoxue],
        Args["bind_name", str],
        help_text="为乌蒙账号绑定对应账号",
    ),
    Subcommand(
        "current",
        Args["profile?", str],
        help_text="查看当前使用的乌蒙账号的信息"
    ),
    Subcommand(
        "update",
        Args["source?", alias_divingfish + alias_luoxue],
        help_text="更新查分器",
    ),
    Subcommand(
        "b50",
        Args["source", alias_divingfish + alias_luoxue],
        help_text="输出自己的b50成绩"
    )
)

if __name__ == "__main__":
    print(maicn_alc.parse("/maicn update"))

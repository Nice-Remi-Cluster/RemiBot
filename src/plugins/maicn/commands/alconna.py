from arclet.alconna import Alconna, Args, Subcommand
from nepattern import AnyString

from src.utils.helpers.alconna_helper import alc_header
from ..alias import alias_divingfish, alias_luoxue

lx_alc = Alconna(
    f"{alc_header}lxns",
    Subcommand(
        "add",
        Args["friend_code", AnyString],
        Args["bind_name?", str],
        help_text="添加落雪账号",
    ),
    Subcommand(
        "create",
        help_text="为绑定的好友码创建对应的落雪档案",
    ),
)

divingfish_alc = Alconna(
    f"{alc_header}divingfish",
    Subcommand(
        "add",
        Args["username", str],
        Args["password", str],
        Args["bind_name?", str],
        help_text="使用账号密码添加水鱼账号",
    ),
)


maicn_alc = Alconna(
    f"{alc_header}maicn",
    Subcommand(
        "add",
        Args["sgwcmaid", str],
        Args["bind_name?", str],
        help_text="添加国区舞萌账号",
    ),
    Subcommand(
        "bind",
        Args["source", alias_divingfish + alias_luoxue],
        Args["bind_name", str],
        help_text="为乌蒙账号绑定对应账号",
    ),
    Subcommand(
        "current", Args["profile?", str], help_text="查看当前使用的乌蒙账号的信息"
    ),
    Subcommand(
        "update",
        Args["source?", alias_divingfish + alias_luoxue],
        help_text="更新查分器",
    ),
    Subcommand(
        "b50",
        Args["source", alias_divingfish + alias_luoxue],
        help_text="输出自己的b50成绩",
    ),
)

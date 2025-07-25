"""权限管理命令定义

使用Alconna定义权限管理相关的命令。
"""

from arclet.alconna import Alconna, Subcommand, Option, Args
from arclet.alconna.args import Field
from nepattern import AnyString
from src.utils.helpers.alconna_helper import alc_header

# 权限管理主命令
permission_alc = Alconna(
    f"{alc_header}permission",
    Subcommand(
        "add_role",
        Args["user_id", AnyString],
        Args["role", str],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand(
        "remove_role",
        Args["user_id", AnyString],
        Args["role", str],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand(
        "list_roles",
        Args["user_id", AnyString],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand(
        "list_users",
        Args["role", str],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand("reload"),
    Subcommand("check"),
    Subcommand("info"),
    Subcommand(
        "add_blacklist",
        Args["user_id", AnyString],
        Args["resource", str],
        Args["action", str, Field(default="*")],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand(
        "remove_blacklist",
        Args["user_id", AnyString],
        Args["resource", str],
        Args["action", str, Field(default="*")],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
    Subcommand(
        "list_blacklist",
        Args["user_id", AnyString],
        Option("--scope", Args["scope", str]),
        Option("--scope-id", Args["scope_id", AnyString]),
    ),
)

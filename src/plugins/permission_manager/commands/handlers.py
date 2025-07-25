"""权限管理命令处理器

处理权限管理相关的命令。
"""

from nonebot import logger
from nonebot.adapters.onebot.v11.event import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from arclet.alconna import SubcommandResult
from nonebot_plugin_alconna import Query as AlcQuery

from ..core import permission_manager, admin_only, PermissionScope
from .matchers import permission_matcher


@permission_matcher.assign("add_role")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("add_role", 0)):
    """为用户添加角色"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    role = r.args["role"]
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 添加角色
    success = permission_manager.add_role_for_user(user_id, role, scope, scope_id)

    if success:
        scope_info = f"在{scope.value}"
        if scope_id:
            scope_info += f" {scope_id}"
        await permission_matcher.finish(
            f"✅ 成功为用户 {user_id} {scope_info} 添加角色 {role}"
        )
    else:
        await permission_matcher.finish(f"❌ 为用户 {user_id} 添加角色 {role} 失败")


@permission_matcher.assign("remove_role")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("remove_role", 0)):
    """移除用户角色"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    role = r.args["role"]
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 移除角色
    success = permission_manager.remove_role_for_user(user_id, role, scope, scope_id)

    if success:
        scope_info = f"在{scope.value}"
        if scope_id:
            scope_info += f" {scope_id}"
        await permission_matcher.finish(
            f"✅ 成功为用户 {user_id} {scope_info} 移除角色 {role}"
        )
    else:
        await permission_matcher.finish(f"❌ 为用户 {user_id} 移除角色 {role} 失败")


@permission_matcher.assign("list_roles")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("list_roles", 0)):
    """列出用户角色"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 获取用户角色
    roles = permission_manager.get_roles_for_user(user_id, scope, scope_id)

    scope_info = f"在{scope.value}"
    if scope_id:
        scope_info += f" {scope_id}"

    if roles:
        roles_text = "\n".join([f"  • {role}" for role in roles])
        message = f"👤 用户 {user_id} {scope_info} 的角色：\n{roles_text}"
    else:
        message = f"👤 用户 {user_id} {scope_info} 没有任何角色"

    await permission_matcher.finish(message)


@permission_matcher.assign("list_users")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("list_users", 0)):
    """列出拥有指定角色的用户"""
    r: SubcommandResult = alc_result.result
    role = r.args["role"]
    scope_str = r.options.get("scope", {"args": {"scope": "global"}}).args.get(
        "scope", "global"
    )
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 获取拥有角色的用户
    users = permission_manager.get_users_for_role(role, scope, scope_id)

    scope_info = f"在{scope.value}"
    if scope_id:
        scope_info += f" {scope_id}"

    if users:
        users_text = "\n".join([f"  • {user}" for user in users])
        message = f"👥 {scope_info} 拥有角色 {role} 的用户：\n{users_text}"
    else:
        message = f"👥 {scope_info} 没有用户拥有角色 {role}"

    await permission_matcher.finish(message)


@permission_matcher.assign("reload")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("reload", 0)):
    """重新加载权限策略"""
    if permission_manager.reload_policy():
        await permission_matcher.finish("✅ 权限策略重新加载成功")
    else:
        await permission_matcher.finish("❌ 权限策略重新加载失败")


@permission_matcher.assign("check")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("check", 0)):
    """检查自己的权限"""
    user_id = event.get_user_id()

    message_parts = [f"👤 您的权限信息："]

    # 检查全局权限
    global_roles = permission_manager.get_roles_for_user(
        user_id, PermissionScope.GLOBAL
    )
    if global_roles:
        message_parts.append(f"\n🌐 全局角色：")
        for role in global_roles:
            message_parts.append(f"  • {role}")

    # 检查私聊权限
    private_roles = permission_manager.get_roles_for_user(
        user_id, PermissionScope.PRIVATE
    )
    if private_roles:
        message_parts.append(f"\n💬 私聊角色：")
        for role in private_roles:
            message_parts.append(f"  • {role}")

    # 如果是群组消息，检查群组权限
    if isinstance(event, GroupMessageEvent):
        group_roles = permission_manager.get_roles_for_user(
            user_id, PermissionScope.GROUP, str(event.group_id)
        )
        if group_roles:
            message_parts.append(f"\n👥 群组 {event.group_id} 角色：")
            for role in group_roles:
                message_parts.append(f"  • {role}")

    if len(message_parts) == 1:
        message_parts.append("\n❌ 您没有任何角色")

    await permission_matcher.finish("".join(message_parts))


@permission_matcher.assign("info")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("info", 0)):
    """显示权限系统信息"""
    message = [
        "🔐 权限管理系统信息",
        "",
        "📋 支持的权限范围：",
        "  • global - 全局权限",
        "  • group - 群组权限",
        "  • private - 私聊权限",
        "",
        "👑 内置角色：",
        "  • admin - 管理员（拥有所有权限）",
        "  • guest - 访客（拥有所有功能权限）",
        "",
        "🚫 黑名单功能：",
        "  • 支持为特定用户禁用特定功能",
        "  • 黑名单优先于角色权限",
        "  • 可按范围（全局/群组/私聊）设置",
        "",
        "💡 使用提示：",
        "  • 群组权限优先于全局权限",
        "  • 私聊权限独立于群组权限",
        "  • 管理员可以管理所有权限",
        "",
        "📖 更多信息请查看文档",
    ]

    await permission_matcher.finish("\n".join(message))


@permission_matcher.assign("add_blacklist")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("add_blacklist", 0)):
    """为用户添加黑名单"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    resource = r.args["resource"]
    action = r.args.get("action", "*")
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 添加黑名单
    success = permission_manager.add_blacklist(
        user_id, resource, action, scope, scope_id
    )

    if success:
        scope_info = f"在{scope.value}"
        if scope_id:
            scope_info += f" {scope_id}"
        await permission_matcher.finish(
            f"✅ 成功为用户 {user_id} {scope_info} 添加黑名单: {resource}:{action}"
        )
    else:
        await permission_matcher.finish(f"❌ 为用户 {user_id} 添加黑名单失败")


@permission_matcher.assign("remove_blacklist")
@admin_only
async def _(
    event: MessageEvent, alc_result: AlcQuery = AlcQuery("remove_blacklist", 0)
):
    """移除用户黑名单"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    resource = r.args["resource"]
    action = r.args.get("action", "*")
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 移除黑名单
    success = permission_manager.remove_blacklist(
        user_id, resource, action, scope, scope_id
    )

    if success:
        scope_info = f"在{scope.value}"
        if scope_id:
            scope_info += f" {scope_id}"
        await permission_matcher.finish(
            f"✅ 成功为用户 {user_id} {scope_info} 移除黑名单: {resource}:{action}"
        )
    else:
        await permission_matcher.finish(f"❌ 为用户 {user_id} 移除黑名单失败")


@permission_matcher.assign("list_blacklist")
@admin_only
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("list_blacklist", 0)):
    """查看用户黑名单"""
    r: SubcommandResult = alc_result.result
    user_id = r.args["user_id"]
    scope_option = r.options.get("scope")
    scope_str = scope_option.args.get("scope", "global") if scope_option else "global"
    scope_id = None

    if "scope_id" in r.options:
        scope_id = r.options["scope_id"].args.get("scope_id")

    # 解析权限范围
    try:
        scope = PermissionScope(scope_str)
    except ValueError:
        await permission_matcher.finish(
            "❌ 无效的权限范围，支持的范围: global, group, private"
        )
        return

    # 如果是群组权限但没有提供群组ID，使用当前群组
    if scope == PermissionScope.GROUP:
        if not scope_id and isinstance(event, GroupMessageEvent):
            scope_id = str(event.group_id)
        elif not scope_id:
            await permission_matcher.finish("❌ 群组权限需要指定群组ID")
            return

    # 获取用户黑名单
    blacklist = permission_manager.get_user_blacklist(user_id, scope, scope_id)

    scope_info = f"在{scope.value}"
    if scope_id:
        scope_info += f" {scope_id}"

    if blacklist:
        blacklist_text = "\n".join([f"  • {item}" for item in blacklist])
        message = f"🚫 用户 {user_id} {scope_info} 的黑名单：\n{blacklist_text}"
    else:
        message = f"🚫 用户 {user_id} {scope_info} 没有任何黑名单"

    await permission_matcher.finish(message)

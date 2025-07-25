"""权限装饰器模块

提供用于命令权限检查的装饰器函数，支持群组和个人的分别权限管理。
"""

from functools import wraps
from typing import Callable, Any

from nonebot import logger
from nonebot.adapters.onebot.v11.event import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher

from .manager import permission_manager
from .models import PermissionContext, PermissionScope


def require_permission(resource: str, action: str):
    """权限检查装饰器

    支持群组和个人的分别权限管理。

    Args:
        resource: 资源名称 (如: maicn, lxns, divingfish)
        action: 操作名称 (如: add, bind, current, update, b50)

    Usage:
        @require_permission("maicn", "add")
        async def add_maicn_account(event: MessageEvent, ...):
            # 命令处理逻辑
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中提取MessageEvent
            event = None
            matcher = None

            # 先从位置参数中查找
            for arg in args:
                if isinstance(arg, MessageEvent):
                    event = arg
                elif isinstance(arg, Matcher):
                    matcher = arg

            # 如果位置参数中没有找到，再从关键字参数中查找
            if not event:
                for key, value in kwargs.items():
                    if isinstance(value, MessageEvent):
                        event = value
                        break
                    elif isinstance(value, Matcher):
                        matcher = value

            if not event:
                logger.warning(f"权限检查装饰器无法找到MessageEvent参数")
                return await func(*args, **kwargs)

            # 创建权限上下文
            context = permission_manager.create_context_from_event(
                event, resource, action
            )

            # 检查权限
            if not permission_manager.check_permission(context):
                user_id = event.get_user_id()
                scope_info = ""

                if isinstance(event, GroupMessageEvent):
                    scope_info = f"群组 {event.group_id} 中"
                elif isinstance(event, PrivateMessageEvent):
                    scope_info = "私聊中"

                error_msg = f"❌ 权限不足\n用户 {user_id} 在{scope_info}没有执行 {resource}.{action} 的权限"
                logger.warning(
                    f"权限检查失败: {context.get_subject()} -> {context.get_object()}"
                )

                if matcher:
                    await matcher.finish(error_msg)
                else:
                    raise FinishedException(error_msg)

            # 权限检查通过，执行原函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def admin_only(func: Callable) -> Callable:
    """仅管理员可用装饰器

    支持群组和个人的分别权限管理。

    Usage:
        @admin_only
        async def admin_command(event: MessageEvent, ...):
            # 管理员专用命令处理逻辑
            pass
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从参数中提取MessageEvent
        event = None
        matcher = None

        # 先从位置参数中查找
        for arg in args:
            if isinstance(arg, MessageEvent):
                event = arg
            elif isinstance(arg, Matcher):
                matcher = arg

        # 如果位置参数中没有找到，再从关键字参数中查找
        if not event:
            for key, value in kwargs.items():
                if isinstance(value, MessageEvent):
                    event = value
                    break
                elif isinstance(value, Matcher):
                    matcher = value

        if not event:
            logger.warning(f"管理员权限检查装饰器无法找到MessageEvent参数")
            return await func(*args, **kwargs)

        user_id = event.get_user_id()

        # 检查是否为管理员
        is_admin = False

        if isinstance(event, GroupMessageEvent):
            # 检查群组管理员权限
            roles = permission_manager.get_roles_for_user(
                user_id, PermissionScope.GROUP, str(event.group_id)
            )
            is_admin = any(role.startswith("admin") for role in roles)

            # 如果不是群组管理员，检查全局管理员权限
            if not is_admin:
                global_roles = permission_manager.get_roles_for_user(
                    user_id, PermissionScope.GLOBAL
                )
                is_admin = "admin" in global_roles

        elif isinstance(event, PrivateMessageEvent):
            # 对于私聊，直接检查全局管理员权限
            global_roles = permission_manager.get_roles_for_user(
                user_id, PermissionScope.GLOBAL
            )
            logger.debug(f"用户 {user_id} 的全局角色: {global_roles}")
            is_admin = "admin" in global_roles
        else:
            # 其他情况检查全局管理员权限
            roles = permission_manager.get_roles_for_user(
                user_id, PermissionScope.GLOBAL
            )
            is_admin = "admin" in roles

        if not is_admin:
            scope_info = ""
            if isinstance(event, GroupMessageEvent):
                scope_info = f"群组 {event.group_id} 中"
            elif isinstance(event, PrivateMessageEvent):
                scope_info = "私聊中"

            error_msg = (
                f"❌ 权限不足\n用户 {user_id} 在{scope_info}不是管理员，无法执行此操作"
            )
            logger.warning(f"管理员权限检查失败: 用户 {user_id} 不是管理员")

            if matcher:
                await matcher.finish(error_msg)
            else:
                raise FinishedException(error_msg)

        # 权限检查通过，执行原函数
        return await func(*args, **kwargs)

    return wrapper


def check_user_permission(event: MessageEvent, resource: str, action: str) -> bool:
    """直接检查用户权限的辅助函数

    Args:
        event: 消息事件
        resource: 资源名称
        action: 操作名称

    Returns:
        bool: 是否有权限
    """
    context = permission_manager.create_context_from_event(event, resource, action)
    return permission_manager.check_permission(context)

"""权限管理器

提供基于Casbin的RBAC权限控制功能，支持群组和个人的分别权限管理。
"""

import os
from pathlib import Path
from typing import List, Optional

import casbin
from nonebot import logger
from nonebot.adapters.onebot.v11.event import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from .models import PermissionContext, PermissionScope
from ..config import MODEL_PATH, POLICY_PATH


class PermissionManager:
    """权限管理器

    支持群组和个人的分别权限管理。
    """

    def __init__(self):
        self.enforcer: Optional[casbin.Enforcer] = None
        self._init_enforcer()

    def _init_enforcer(self):
        """初始化Casbin执行器"""
        try:
            if not MODEL_PATH.exists():
                logger.error(f"权限模型文件不存在: {MODEL_PATH}")
                return False

            if not POLICY_PATH.exists():
                logger.error(f"权限策略文件不存在: {POLICY_PATH}")
                return False

            # 初始化Casbin执行器
            self.enforcer = casbin.Enforcer(str(MODEL_PATH), str(POLICY_PATH))
            logger.success("权限管理器初始化成功")

        except Exception as e:
            logger.error(f"权限管理器初始化失败: {e}")

    def create_context_from_event(
        self, event: MessageEvent, resource: str, action: str
    ) -> PermissionContext:
        """从事件创建权限上下文

        Args:
            event: 消息事件
            resource: 资源名称
            action: 操作名称

        Returns:
            PermissionContext: 权限上下文
        """
        user_id = event.get_user_id()

        if isinstance(event, GroupMessageEvent):
            return PermissionContext(
                user_id=user_id,
                scope=PermissionScope.GROUP,
                scope_id=str(event.group_id),
                resource=resource,
                action=action,
            )
        elif isinstance(event, PrivateMessageEvent):
            return PermissionContext(
                user_id=user_id,
                scope=PermissionScope.PRIVATE,
                resource=resource,
                action=action,
            )
        else:
            # 默认为全局权限
            return PermissionContext(
                user_id=user_id,
                scope=PermissionScope.GLOBAL,
                resource=resource,
                action=action,
            )

    def check_permission(self, context: PermissionContext) -> bool:
        """检查权限

        Args:
            context: 权限上下文

        Returns:
            bool: 是否有权限
        """
        if not self.enforcer:
            logger.warning("Casbin执行器未初始化，默认允许所有操作")
            return True

        try:
            subject = context.user_id
            obj = f"{context.resource}:{context.action}"
            act = "access"
            scope = context.scope.value
            scope_id = context.scope_id or "*"

            # 检查权限 - 传递5个参数匹配模型定义
            result = self.enforcer.enforce(subject, obj, act, scope, scope_id)

            logger.debug(
                f"权限检查: {subject} -> {obj} (scope: {scope}, scope_id: {scope_id}) = {result}"
            )
            return result

        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            return False

    def add_role_for_user(
        self,
        user_id: str,
        role: str,
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> bool:
        """为用户添加角色

        Args:
            user_id: 用户ID
            role: 角色名称
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            bool: 是否添加成功
        """
        if not self.enforcer:
            return False

        try:
            context = PermissionContext(user_id=user_id, scope=scope, scope_id=scope_id)
            subject = context.get_subject()

            # 构造角色名称，包含范围信息
            if scope == PermissionScope.GROUP and scope_id:
                role_name = f"{role}@{scope_id}"
            else:
                role_name = role

            success = self.enforcer.add_role_for_user(subject, role_name)
            if success:
                self.enforcer.save_policy()
                logger.info(f"为用户 {subject} 添加角色 {role_name} 成功")
            return success

        except Exception as e:
            logger.error(f"添加用户角色失败: {e}")
            return False

    def remove_role_for_user(
        self,
        user_id: str,
        role: str,
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> bool:
        """移除用户角色

        Args:
            user_id: 用户ID
            role: 角色名称
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            bool: 是否移除成功
        """
        if not self.enforcer:
            return False

        try:
            context = PermissionContext(user_id=user_id, scope=scope, scope_id=scope_id)
            subject = context.get_subject()

            # 构造角色名称，包含范围信息
            if scope == PermissionScope.GROUP and scope_id:
                role_name = f"{role}@{scope_id}"
            else:
                role_name = role

            success = self.enforcer.remove_role_for_user(subject, role_name)
            if success:
                self.enforcer.save_policy()
                logger.info(f"为用户 {subject} 移除角色 {role_name} 成功")
            return success

        except Exception as e:
            logger.error(f"移除用户角色失败: {e}")
            return False

    def get_roles_for_user(
        self,
        user_id: str,
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> List[str]:
        """获取用户的所有角色

        Args:
            user_id: 用户ID
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            List[str]: 角色列表
        """
        if not self.enforcer:
            return []

        try:
            # 直接查询grouping policy来获取角色
            grouping_policy = self.enforcer.get_grouping_policy()
            roles = []

            for policy in grouping_policy:
                if len(policy) >= 4:
                    policy_user = policy[0]
                    policy_role = policy[1]
                    policy_scope = policy[2]
                    policy_scope_id = policy[3]

                    # 检查用户ID匹配
                    if policy_user == user_id:
                        # 检查范围匹配
                        if policy_scope == scope.value:
                            # 检查范围ID匹配
                            if (
                                scope_id is None
                                or policy_scope_id == scope_id
                                or policy_scope_id == "*"
                            ):
                                roles.append(policy_role)

            logger.debug(f"用户 {user_id} 在 {scope.value} 范围的角色: {roles}")
            return roles

        except Exception as e:
            logger.error(f"获取用户角色失败: {e}")
            return []

    def get_users_for_role(
        self, role: str, scope: PermissionScope, scope_id: Optional[str] = None
    ) -> List[str]:
        """获取拥有指定角色的用户列表"""
        if not self.enforcer:
            return []

        # 获取所有角色分配
        grouping_policy = self.enforcer.get_grouping_policy()
        users = []

        for policy in grouping_policy:
            if len(policy) >= 4 and policy[1] == role and policy[2] == scope.value:
                if scope_id is None or policy[3] == scope_id or policy[3] == "*":
                    users.append(policy[0])

        return users

    def reload_policy(self) -> bool:
        """重新加载权限策略

        Returns:
            bool: 是否重新加载成功
        """
        if not self.enforcer:
            return False

        try:
            self.enforcer.load_policy()
            logger.info("权限策略重新加载成功")
            return True
        except Exception as e:
            logger.error(f"权限策略重新加载失败: {e}")
            return False

    def add_blacklist(
        self,
        user_id: str,
        resource: str,
        action: str = "*",
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> bool:
        """为用户添加黑名单（拒绝策略）

        Args:
            user_id: 用户ID
            resource: 资源名称（功能名）
            action: 操作名称，默认为*（所有操作）
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            bool: 是否添加成功
        """
        if not self.enforcer:
            return False

        try:
            obj = f"{resource}:{action}"
            act = "access"
            scope_val = scope.value
            scope_id_val = scope_id or "*"

            # 添加拒绝策略
            success = self.enforcer.add_policy(
                user_id, obj, act, scope_val, scope_id_val, "deny"
            )
            if success:
                self.enforcer.save_policy()
                logger.info(
                    f"为用户 {user_id} 添加黑名单: {resource}:{action} (scope: {scope_val}, scope_id: {scope_id_val})"
                )
            return success

        except Exception as e:
            logger.error(f"添加黑名单失败: {e}")
            return False

    def remove_blacklist(
        self,
        user_id: str,
        resource: str,
        action: str = "*",
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> bool:
        """移除用户黑名单（拒绝策略）

        Args:
            user_id: 用户ID
            resource: 资源名称（功能名）
            action: 操作名称，默认为*（所有操作）
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            bool: 是否移除成功
        """
        if not self.enforcer:
            return False

        try:
            obj = f"{resource}:{action}"
            act = "access"
            scope_val = scope.value
            scope_id_val = scope_id or "*"

            # 移除拒绝策略
            success = self.enforcer.remove_policy(
                user_id, obj, act, scope_val, scope_id_val, "deny"
            )
            if success:
                self.enforcer.save_policy()
                logger.info(
                    f"为用户 {user_id} 移除黑名单: {resource}:{action} (scope: {scope_val}, scope_id: {scope_id_val})"
                )
            return success

        except Exception as e:
            logger.error(f"移除黑名单失败: {e}")
            return False

    def get_user_blacklist(
        self,
        user_id: str,
        scope: PermissionScope = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> List[str]:
        """获取用户的黑名单

        Args:
            user_id: 用户ID
            scope: 权限范围
            scope_id: 范围ID（群组ID）

        Returns:
            List[str]: 黑名单列表（格式：resource:action）
        """
        if not self.enforcer:
            return []

        try:
            # 获取所有策略
            policies = self.enforcer.get_policy()
            blacklist = []

            for policy in policies:
                if len(policy) >= 6:
                    policy_user = policy[0]
                    policy_obj = policy[1]
                    policy_act = policy[2]
                    policy_scope = policy[3]
                    policy_scope_id = policy[4]
                    policy_eft = policy[5]

                    # 检查是否为拒绝策略且用户匹配
                    if (
                        policy_user == user_id
                        and policy_eft == "deny"
                        and policy_scope == scope.value
                        and (
                            scope_id is None
                            or policy_scope_id == scope_id
                            or policy_scope_id == "*"
                        )
                    ):
                        blacklist.append(policy_obj)

            logger.debug(f"用户 {user_id} 在 {scope.value} 范围的黑名单: {blacklist}")
            return blacklist

        except Exception as e:
            logger.error(f"获取用户黑名单失败: {e}")
            return []


# 全局权限管理器实例
permission_manager = PermissionManager()

"""权限管理数据模型

定义权限管理相关的数据结构。
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class PermissionScope(Enum):
    """权限范围枚举"""
    GLOBAL = "global"  # 全局权限
    GROUP = "group"    # 群组权限
    PRIVATE = "private" # 私聊权限


@dataclass
class PermissionContext:
    """权限上下文
    
    用于描述权限检查的完整上下文信息。
    """
    user_id: str
    scope: PermissionScope
    scope_id: Optional[str] = None  # 群组ID（当scope为GROUP时）
    resource: str = ""
    action: str = ""
    
    def get_subject(self) -> str:
        """获取权限主体标识符
        
        Returns:
            str: 权限主体标识符，格式为 user_id 或 user_id@group_id
        """
        if self.scope == PermissionScope.GROUP and self.scope_id:
            return f"{self.user_id}@{self.scope_id}"
        return self.user_id
    
    def get_object(self) -> str:
        """获取权限对象标识符
        
        Returns:
            str: 权限对象标识符，格式为 scope:resource:action
        """
        return f"{self.scope.value}:{self.resource}:{self.action}"
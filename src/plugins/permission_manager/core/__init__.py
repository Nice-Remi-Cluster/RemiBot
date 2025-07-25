"""权限管理核心模块

提供权限管理的核心功能。
"""

from .manager import permission_manager
from .decorators import require_permission, admin_only, check_user_permission
from .models import PermissionContext, PermissionScope

__all__ = [
    "permission_manager",
    "require_permission", 
    "admin_only",
    "check_user_permission",
    "PermissionContext",
    "PermissionScope",
]
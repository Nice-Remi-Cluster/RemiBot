"""冷却时间管理服务"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple

from nonebot_plugin_orm import get_session
from sqlalchemy import select, update

from ..models import NiuniuCooldown, OperationType
from .database import DatabaseService


class CooldownManager:
    """冷却时间管理类"""
    
    COOLDOWN_MINUTES = 10
    MAX_DAILY_TARGETED = 3
    
    @classmethod
    async def check_cooldown(cls, user_id: str, group_id: str, operation_type: str) -> Tuple[bool, int]:
        """检查冷却时间
        
        Args:
            user_id: 用户ID
            group_id: 群组ID
            operation_type: 操作类型 ("dao" 或 "ri")
            
        Returns:
            tuple: (是否可以操作, 剩余冷却时间分钟数)
        """
        cooldown_data = await DatabaseService.get_cooldown_data(user_id, group_id)
        
        if cooldown_data is None:
            return True, 0
        
        now = datetime.now()
        last_operation_time = None
        
        if operation_type == "dao":
            last_operation_time = cooldown_data.last_dao_time
        elif operation_type == "ri":
            last_operation_time = cooldown_data.last_ri_time
        
        if last_operation_time is None:
            return True, 0
        
        time_diff = now - last_operation_time
        cooldown_seconds = cls.COOLDOWN_MINUTES * 60
        
        if time_diff.total_seconds() >= cooldown_seconds:
            return True, 0
        else:
            remaining_seconds = cooldown_seconds - time_diff.total_seconds()
            remaining_minutes = int(remaining_seconds / 60) + 1
            return False, remaining_minutes
    
    @classmethod
    async def update_cooldown(cls, user_id: str, group_id: str, operation_type: str) -> None:
        """更新冷却时间
        
        Args:
            user_id: 用户ID
            group_id: 群组ID
            operation_type: 操作类型 ("dao" 或 "ri")
        """
        now = datetime.now()
        
        if operation_type == "dao":
            await DatabaseService.update_cooldown_data(
                user_id, group_id, last_dao_time=now
            )
        elif operation_type == "ri":
            await DatabaseService.update_cooldown_data(
                user_id, group_id, last_ri_time=now
            )
    
    @classmethod
    async def check_daily_limit(cls, user_id: str, group_id: str) -> bool:
        """检查每日被指定次数限制
        
        Args:
            user_id: 用户ID
            group_id: 群组ID
            
        Returns:
            bool: 是否可以被指定
        """
        cooldown_data = await DatabaseService.get_cooldown_data(user_id, group_id)
        
        if cooldown_data is None:
            return True
        
        today = date.today()
        
        # 如果是新的一天，重置计数
        if cooldown_data.last_reset_date != today:
            await DatabaseService.update_cooldown_data(
                user_id, group_id, 
                daily_targeted_count=0, 
                last_reset_date=today
            )
            return True
        
        # 检查是否超过每日限制
        return cooldown_data.daily_targeted_count < cls.MAX_DAILY_TARGETED
    
    @classmethod
    async def increment_daily_targeted(cls, user_id: str, group_id: str) -> None:
        """增加每日被指定次数
        
        Args:
            user_id: 用户ID
            group_id: 群组ID
        """
        cooldown_data = await DatabaseService.get_cooldown_data(user_id, group_id)
        today = date.today()
        
        if cooldown_data is None:
            await DatabaseService.update_cooldown_data(
                user_id, group_id,
                daily_targeted_count=1,
                last_reset_date=today
            )
        else:
            # 如果是新的一天，重置计数
            if cooldown_data.last_reset_date != today:
                new_count = 1
            else:
                new_count = cooldown_data.daily_targeted_count + 1
            
            await DatabaseService.update_cooldown_data(
                user_id, group_id,
                daily_targeted_count=new_count,
                last_reset_date=today
            )
    
    @classmethod
    def format_remaining_time(cls, minutes: int) -> str:
        """格式化剩余时间显示
        
        Args:
            minutes: 剩余分钟数
            
        Returns:
            str: 格式化后的时间字符串
        """
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes > 0:
                return f"{hours}小时{remaining_minutes}分钟"
            else:
                return f"{hours}小时"
        else:
            return f"{minutes}分钟"
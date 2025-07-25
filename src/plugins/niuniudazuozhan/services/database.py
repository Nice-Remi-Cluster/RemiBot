"""数据库服务类"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from nonebot_plugin_orm import get_session
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserNiuniuData, NiuniuOperation, NiuniuCooldown, OperationType


class DatabaseService:
    """数据库服务类"""
    
    @staticmethod
    async def get_user_data(user_id: str, group_id: str) -> Optional[UserNiuniuData]:
        """获取用户数据"""
        async with get_session() as session:
            result = await session.execute(
                select(UserNiuniuData).where(
                    UserNiuniuData.user_id == user_id,
                    UserNiuniuData.group_id == group_id
                )
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_or_update_user_data(
        user_id: str, 
        group_id: str, 
        length_change: Decimal
    ) -> UserNiuniuData:
        """创建或更新用户数据"""
        async with get_session() as session:
            user_data = await DatabaseService.get_user_data(user_id, group_id)
            
            if user_data is None:
                user_data = UserNiuniuData(
                    user_id=user_id,
                    group_id=group_id,
                    length=length_change,
                    total_operations=1,
                    last_operation_time=datetime.now()
                )
                session.add(user_data)
            else:
                user_data.length += length_change
                user_data.total_operations += 1
                user_data.last_operation_time = datetime.now()
            
            await session.commit()
            await session.refresh(user_data)
            return user_data
    
    @staticmethod
    async def record_operation(
        user_id: str,
        group_id: str,
        operation_type: OperationType,
        length_change: Decimal,
        target_user_id: Optional[str] = None,
        target_length_change: Optional[Decimal] = None
    ) -> NiuniuOperation:
        """记录操作"""
        async with get_session() as session:
            operation = NiuniuOperation(
                user_id=user_id,
                group_id=group_id,
                target_user_id=target_user_id,
                operation_type=operation_type,
                length_change=length_change,
                target_length_change=target_length_change
            )
            session.add(operation)
            await session.commit()
            await session.refresh(operation)
            return operation
    
    @staticmethod
    async def get_cooldown_data(user_id: str, group_id: str) -> Optional[NiuniuCooldown]:
        """获取冷却时间数据"""
        async with get_session() as session:
            result = await session.execute(
                select(NiuniuCooldown).where(
                    NiuniuCooldown.user_id == user_id,
                    NiuniuCooldown.group_id == group_id
                )
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_cooldown_data(
        user_id: str,
        group_id: str,
        last_dao_time: Optional[datetime] = None,
        last_ri_time: Optional[datetime] = None,
        daily_targeted_count: Optional[int] = None,
        last_reset_date: Optional[date] = None
    ) -> NiuniuCooldown:
        """更新冷却时间数据"""
        async with get_session() as session:
            cooldown_data = await DatabaseService.get_cooldown_data(user_id, group_id)
            
            if cooldown_data is None:
                cooldown_data = NiuniuCooldown(
                    user_id=user_id,
                    group_id=group_id,
                    last_dao_time=last_dao_time,
                    last_ri_time=last_ri_time,
                    daily_targeted_count=daily_targeted_count or 0,
                    last_reset_date=last_reset_date
                )
                session.add(cooldown_data)
            else:
                if last_dao_time is not None:
                    cooldown_data.last_dao_time = last_dao_time
                if last_ri_time is not None:
                    cooldown_data.last_ri_time = last_ri_time
                if daily_targeted_count is not None:
                    cooldown_data.daily_targeted_count = daily_targeted_count
                if last_reset_date is not None:
                    cooldown_data.last_reset_date = last_reset_date
            
            await session.commit()
            await session.refresh(cooldown_data)
            return cooldown_data
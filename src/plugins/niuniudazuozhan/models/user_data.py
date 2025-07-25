"""用户数据模型定义"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from enum import Enum

from nonebot_plugin_orm import Model
from sqlalchemy import String, DECIMAL, DateTime, Date, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class OperationType(str, Enum):
    """操作类型枚举"""
    DAO = "dao"
    RI_QUNYU = "ri_qunyu"


class UserNiuniuData(Model):
    """用户牛牛数据模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    length: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal('0.00'), comment="牛牛长度(cm)"
    )
    total_operations: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总操作次数"
    )
    last_operation_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后操作时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index('uk_user_data_user_group', 'user_id', 'group_id', unique=True),
        Index('idx_user_data_group_id', 'group_id'),
        Index('idx_user_data_last_operation', 'last_operation_time'),
    )


class NiuniuOperation(Model):
    """牛牛操作记录模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    target_user_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="目标用户ID（日群友时使用）"
    )
    operation_type: Mapped[OperationType] = mapped_column(
        nullable=False, comment="操作类型"
    )
    length_change: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="长度变化"
    )
    target_length_change: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, comment="目标用户长度变化"
    )
    operation_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    
    __table_args__ = (
        Index('idx_operation_user_group_time', 'user_id', 'group_id', 'operation_time'),
        Index('idx_operation_target_user_time', 'target_user_id', 'operation_time'),
    )


class NiuniuCooldown(Model):
    """冷却时间模型"""
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户ID")
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="群组ID")
    last_dao_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后导操作时间"
    )
    last_ri_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后日群友时间"
    )
    daily_targeted_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="今日被指定次数"
    )
    last_reset_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="最后重置日期"
    )
    
    __table_args__ = (
        Index('uk_cooldown_user_group', 'user_id', 'group_id', unique=True),
    )
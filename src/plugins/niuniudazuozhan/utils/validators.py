"""数据验证工具"""

import re
from typing import Optional
from decimal import Decimal, InvalidOperation


class Validators:
    """数据验证器类"""
    
    @staticmethod
    def is_valid_user_id(user_id: str) -> bool:
        """验证用户ID格式
        
        Args:
            user_id: 用户ID字符串
            
        Returns:
            bool: 是否为有效的用户ID
        """
        if not user_id or not isinstance(user_id, str):
            return False
        
        # QQ号通常是5-11位数字
        return re.match(r'^\d{5,11}$', user_id) is not None
    
    @staticmethod
    def is_valid_group_id(group_id: str) -> bool:
        """验证群组ID格式
        
        Args:
            group_id: 群组ID字符串
            
        Returns:
            bool: 是否为有效的群组ID
        """
        if not group_id or not isinstance(group_id, str):
            return False
        
        # QQ群号通常是6-12位数字
        return re.match(r'^\d{6,12}$', group_id) is not None
    
    @staticmethod
    def is_valid_length(length: float) -> bool:
        """验证长度值是否合理
        
        Args:
            length: 长度值
            
        Returns:
            bool: 是否为合理的长度值
        """
        # 长度范围：-100cm 到 +100cm
        return -100.0 <= length <= 100.0
    
    @staticmethod
    def sanitize_decimal(value: any, default: Decimal = Decimal('0.00')) -> Decimal:
        """安全转换为Decimal类型
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
            
        Returns:
            Decimal: 转换后的Decimal值
        """
        try:
            if isinstance(value, Decimal):
                return value
            elif isinstance(value, (int, float)):
                return Decimal(str(value))
            elif isinstance(value, str):
                return Decimal(value)
            else:
                return default
        except (InvalidOperation, ValueError):
            return default
    
    @staticmethod
    def sanitize_string(value: any, max_length: int = 255) -> str:
        """安全转换为字符串并限制长度
        
        Args:
            value: 要转换的值
            max_length: 最大长度
            
        Returns:
            str: 转换后的字符串
        """
        if value is None:
            return ""
        
        str_value = str(value)
        return str_value[:max_length] if len(str_value) > max_length else str_value
    
    @staticmethod
    def is_safe_operation_count(count: int) -> bool:
        """验证操作次数是否安全
        
        Args:
            count: 操作次数
            
        Returns:
            bool: 是否为安全的操作次数
        """
        # 操作次数不应超过10000次
        return 0 <= count <= 10000
    
    @staticmethod
    def validate_length_change(change: float) -> bool:
        """验证长度变化值是否合理
        
        Args:
            change: 长度变化值
            
        Returns:
            bool: 是否为合理的变化值
        """
        # 单次变化不应超过±10cm
        return -10.0 <= change <= 10.0
    
    @staticmethod
    def clean_username(username: str) -> str:
        """清理用户名中的特殊字符
        
        Args:
            username: 原始用户名
            
        Returns:
            str: 清理后的用户名
        """
        if not username:
            return "未知用户"
        
        # 移除可能导致问题的字符
        cleaned = re.sub(r'[\r\n\t]', ' ', username)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned[:50] if len(cleaned) > 50 else cleaned
    
    @staticmethod
    def is_valid_cooldown_minutes(minutes: int) -> bool:
        """验证冷却时间分钟数是否合理
        
        Args:
            minutes: 冷却时间分钟数
            
        Returns:
            bool: 是否为合理的冷却时间
        """
        # 冷却时间应在1分钟到24小时之间
        return 1 <= minutes <= 1440
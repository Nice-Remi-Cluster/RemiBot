"""游戏逻辑服务"""

import random
from typing import Tuple


class GameLogic:
    """游戏逻辑类"""
    
    @staticmethod
    def calculate_dao_change() -> float:
        """计算导操作的长度变化
        
        Returns:
            float: 长度变化值，范围 -5.0 到 +5.0 cm
        """
        # 50%概率增长，50%概率缩短
        # 变化范围：-5.0 到 +5.0 cm
        direction = random.choice([-1, 1])
        change = random.uniform(0.1, 5.0) * direction
        return round(change, 2)
    
    @staticmethod
    def calculate_ri_changes() -> Tuple[float, float]:
        """计算日群友操作的长度变化
        
        Returns:
            tuple: (攻击者增加值, 被攻击者减少值)
        """
        # 攻击者增加：0.1-1.0cm
        # 被攻击者减少：0.1-1.0cm
        attacker_gain = random.uniform(0.1, 1.0)
        target_loss = -random.uniform(0.1, 1.0)
        return round(attacker_gain, 2), round(target_loss, 2)
    
    @staticmethod
    def format_length(length: float) -> str:
        """格式化长度显示
        
        Args:
            length: 长度值
            
        Returns:
            str: 格式化后的长度字符串
        """
        if length >= 0:
            return f"{length:.2f}cm"
        else:
            return f"{abs(length):.2f}cm深度"
    
    @staticmethod
    def get_length_description(length: float) -> str:
        """获取长度描述（已取消等级机制）
        
        Args:
            length: 长度值
            
        Returns:
            str: 空字符串（等级机制已移除）
        """
        return ""
    
    @staticmethod
    def is_critical_hit() -> bool:
        """判断是否暴击（10%概率）
        
        Returns:
            bool: 是否暴击
        """
        return random.random() < 0.1
    
    @staticmethod
    def apply_critical_multiplier(value: float, is_critical: bool = False) -> float:
        """应用暴击倍数
        
        Args:
            value: 原始值
            is_critical: 是否暴击
            
        Returns:
            float: 应用暴击后的值
        """
        if is_critical:
            return round(value * 1.5, 2)
        return value
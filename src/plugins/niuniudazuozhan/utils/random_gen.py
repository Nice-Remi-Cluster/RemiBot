"""随机数生成工具"""

import random
from typing import List, Tuple


class RandomGenerator:
    """随机数生成器类"""
    
    @staticmethod
    def random_float(min_val: float, max_val: float, precision: int = 2) -> float:
        """生成指定范围的随机浮点数
        
        Args:
            min_val: 最小值
            max_val: 最大值
            precision: 小数位数
            
        Returns:
            float: 随机浮点数
        """
        return round(random.uniform(min_val, max_val), precision)
    
    @staticmethod
    def random_choice_weighted(choices: List[Tuple[any, float]]) -> any:
        """根据权重随机选择
        
        Args:
            choices: 选择列表，每个元素为 (值, 权重) 的元组
            
        Returns:
            any: 随机选择的值
        """
        total_weight = sum(weight for _, weight in choices)
        rand_num = random.uniform(0, total_weight)
        
        current_weight = 0
        for choice, weight in choices:
            current_weight += weight
            if rand_num <= current_weight:
                return choice
        
        # 如果没有选中任何值，返回最后一个
        return choices[-1][0]
    
    @staticmethod
    def random_bool(probability: float = 0.5) -> bool:
        """根据概率生成随机布尔值
        
        Args:
            probability: 返回 True 的概率 (0.0 - 1.0)
            
        Returns:
            bool: 随机布尔值
        """
        return random.random() < probability
    
    @staticmethod
    def random_gaussian(mean: float, std_dev: float, precision: int = 2) -> float:
        """生成正态分布的随机数
        
        Args:
            mean: 均值
            std_dev: 标准差
            precision: 小数位数
            
        Returns:
            float: 正态分布随机数
        """
        return round(random.gauss(mean, std_dev), precision)
    
    @staticmethod
    def random_sign() -> int:
        """随机生成正负号
        
        Returns:
            int: 1 或 -1
        """
        return random.choice([-1, 1])
    
    @staticmethod
    def random_percentage() -> float:
        """生成0-100的随机百分比
        
        Returns:
            float: 0.00 到 100.00 的随机数
        """
        return round(random.uniform(0, 100), 2)
    
    @staticmethod
    def random_from_range_list(ranges: List[Tuple[float, float]]) -> float:
        """从多个范围中随机选择一个范围，然后在该范围内生成随机数
        
        Args:
            ranges: 范围列表，每个元素为 (最小值, 最大值) 的元组
            
        Returns:
            float: 随机数
        """
        selected_range = random.choice(ranges)
        return RandomGenerator.random_float(selected_range[0], selected_range[1])
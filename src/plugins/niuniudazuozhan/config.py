"""牛牛大作战插件配置文件"""

from decimal import Decimal
from typing import Dict, List, Tuple


class NiuniuConfig:
    """牛牛大作战配置类"""
    
    # 基础配置
    PLUGIN_NAME = "牛牛大作战"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "一个有趣的群聊互动游戏插件"
    
    # 长度配置
    MIN_LENGTH = Decimal('-50.00')  # 最小长度
    MAX_LENGTH = Decimal('100.00')  # 最大长度
    INITIAL_LENGTH = Decimal('10.00')  # 初始长度
    
    # 导操作配置
    DAO_LENGTH_RANGES = [
        (-10.0, -5.0),   # 大幅缩短
        (-5.0, -1.0),    # 中等缩短
        (-1.0, 0.0),     # 轻微缩短
        (0.0, 1.0),      # 轻微增长
        (1.0, 5.0),      # 中等增长
        (5.0, 10.0),     # 大幅增长
    ]
    
    # 日群友操作配置
    RI_ATTACKER_GAIN_RANGE = (1.0, 8.0)    # 攻击者增长范围
    RI_TARGET_LOSS_RANGE = (-8.0, -1.0)    # 被攻击者减少范围
    
    # 暴击配置
    CRITICAL_HIT_CHANCE = 0.1  # 暴击概率 (10%)
    CRITICAL_MULTIPLIER = 1.5  # 暴击倍数
    
    # 冷却时间配置 (分钟)
    COOLDOWN_TIMES = {
        'dao': 30,      # 导操作冷却时间
        'ri': 60,       # 日群友操作冷却时间
        'view': 5,      # 查看操作冷却时间
    }
    
    # 每日限制配置
    DAILY_TARGET_LIMIT = 10  # 每日最多被指定次数
    
    # 长度描述配置已移除（取消等级机制）
    
    # 操作结果消息模板
    DAO_SUCCESS_MESSAGES = [
        "导了一下，",
        "轻轻一导，",
        "用力一导，",
        "小心翼翼地导了导，",
        "随手一导，",
    ]
    
    RI_SUCCESS_MESSAGES = [
        "日群友成功！",
        "攻击得手！",
        "成功发起攻击！",
        "战斗胜利！",
    ]
    
    # 暴击消息
    CRITICAL_HIT_MESSAGES = [
        "💥 暴击！",
        "🔥 会心一击！",
        "⚡ 完美命中！",
        "💫 超级暴击！",
    ]
    
    # 错误消息
    ERROR_MESSAGES = {
        'cooldown': "冷却中，还需等待 {time}",
        'daily_limit': "今天已经被日够了，请明天再试",
        'self_target': "不能日自己！",
        'invalid_user': "用户信息无效",
        'invalid_group': "群组信息无效",
        'operation_failed': "操作失败，请稍后重试",
        'permission_denied': "只有管理员才能使用此功能",
    }
    
    # 帮助信息
    HELP_MESSAGE = """
🎮 牛牛大作战 使用说明

📋 基础命令：
• /nndzz dao 或 "导" - 对自己进行导操作
• /nndzz view 或 "查看牛牛" - 查看自己的牛牛数据
• /nndzz help 或 "牛牛帮助" - 显示此帮助信息

⚔️ 互动命令：
• /nndzz attack @某人 或 "日群友 @某人" - 攻击指定群友
• /nndzz rank 或 "牛牛排行榜" - 查看群内排行榜

🔧 管理命令（仅管理员）：
• /nndzz reset 或 "重置牛牛" - 重置自己的数据
• /nndzz reset @某人 - 重置指定用户的数据

📊 游戏规则：
• 初始长度：{initial_length}cm
• 长度范围：{min_length}cm ~ {max_length}cm
• 导操作冷却：{dao_cooldown}分钟
• 日群友冷却：{ri_cooldown}分钟
• 每日被指定限制：{daily_limit}次
• 暴击概率：{critical_chance}%

💡 小贴士：
• 支持中英文命令
• 仅限群聊使用
• 数据按群独立存储
• 操作有冷却时间限制
""".format(
        initial_length=INITIAL_LENGTH,
        min_length=MIN_LENGTH,
        max_length=MAX_LENGTH,
        dao_cooldown=COOLDOWN_TIMES['dao'],
        ri_cooldown=COOLDOWN_TIMES['ri'],
        daily_limit=DAILY_TARGET_LIMIT,
        critical_chance=int(CRITICAL_HIT_CHANCE * 100)
    )
    
    # 数据库配置
    DB_TABLE_PREFIX = "niuniu_"  # 数据库表前缀
    
    # 安全配置
    MAX_USERNAME_LENGTH = 50  # 最大用户名长度
    MAX_OPERATION_COUNT_PER_HOUR = 100  # 每小时最大操作次数
    
    # 调试配置
    DEBUG_MODE = False  # 调试模式
    LOG_OPERATIONS = True  # 是否记录操作日志
    
    # get_length_description 方法已移除（取消等级机制）
    
    @classmethod
    def get_cooldown_time(cls, operation_type: str) -> int:
        """获取指定操作的冷却时间"""
        return cls.COOLDOWN_TIMES.get(operation_type, 30)
    
    @classmethod
    def is_valid_length(cls, length: Decimal) -> bool:
        """检查长度是否在有效范围内"""
        return cls.MIN_LENGTH <= length <= cls.MAX_LENGTH
    
    @classmethod
    def clamp_length(cls, length: Decimal) -> Decimal:
        """将长度限制在有效范围内"""
        if length < cls.MIN_LENGTH:
            return cls.MIN_LENGTH
        elif length > cls.MAX_LENGTH:
            return cls.MAX_LENGTH
        return length
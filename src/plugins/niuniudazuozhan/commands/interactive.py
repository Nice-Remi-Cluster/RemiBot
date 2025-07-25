"""互动命令处理模块"""

from decimal import Decimal
from typing import Optional

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import Rule
from nonebot_plugin_alconna import Alconna, Subcommand, Args, AlconnaMatcher, Match, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage, At

from ..models import OperationType
from ..services import DatabaseService, GameLogic, CooldownManager
from ..utils import Validators, handle_exceptions, ErrorMessages


def is_group_chat() -> Rule:
    """检查是否为群聊"""
    def _is_group(event: Event) -> bool:
        return isinstance(event, GroupMessageEvent)
    return Rule(_is_group)


# 日群友命令
ri_qunyu_alc = Alconna("/nndzz", Subcommand("attack", Args["target?", At]))
# 添加中文快捷方式
ri_qunyu_alc.shortcut("日群友", {"command": "/nndzz attack"})
ri_qunyu_alc.shortcut("日", {"command": "/nndzz attack"})
# 支持带参数的中文快捷方式
ri_qunyu_alc.shortcut("日群友 (.+)", {"command": "/nndzz attack {0}"})
ri_qunyu_alc.shortcut("日 (.+)", {"command": "/nndzz attack {0}"})

ri_qunyu_cmd = on_alconna(
    ri_qunyu_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)


@ri_qunyu_cmd.assign("attack")
@handle_exceptions
async def handle_ri_qunyu(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    """处理日群友命令"""
    if not target.available:
        await matcher.finish("请指定要日的群友！使用方法：日群友 @某人")
    
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    target_user_id = str(target.result.target)
    
    # 验证用户ID和群组ID
    if not Validators.is_valid_user_id(user_id) or not Validators.is_valid_group_id(group_id):
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    if not Validators.is_valid_user_id(target_user_id):
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    # 不能日自己
    if user_id == target_user_id:
        await matcher.finish("不能日自己！")
    
    # 检查攻击者冷却时间
    can_use, remaining = await CooldownManager.check_cooldown(user_id, group_id, "ri")
    if not can_use:
        remaining_time = CooldownManager.format_remaining_time(remaining)
        await matcher.finish(f"冷却中，还需等待 {remaining_time}")
    
    # 检查目标每日被指定次数
    if not await CooldownManager.check_daily_limit(target_user_id, group_id):
        reply_msg = UniMessage([
            target.result,
            " 今天已经被日够了，请明天再试"
        ])
        await matcher.finish(reply_msg)
    
    # 执行日群友操作
    attacker_gain, target_loss = GameLogic.calculate_ri_changes()
    
    # 检查是否暴击
    is_critical = GameLogic.is_critical_hit()
    if is_critical:
        attacker_gain = GameLogic.apply_critical_multiplier(attacker_gain, True)
        target_loss = GameLogic.apply_critical_multiplier(target_loss, True)
    
    # 验证长度变化值
    if not Validators.validate_length_change(attacker_gain) or not Validators.validate_length_change(target_loss):
        await matcher.finish(ErrorMessages.VALIDATION_ERROR)
    
    # 更新攻击者数据
    attacker_data = await DatabaseService.create_or_update_user_data(
        user_id, group_id, Decimal(str(attacker_gain))
    )
    
    # 更新目标数据
    target_data = await DatabaseService.create_or_update_user_data(
        target_user_id, group_id, Decimal(str(target_loss))
    )
    
    # 记录操作
    await DatabaseService.record_operation(
        user_id, group_id, OperationType.RI_QUNYU, 
        Decimal(str(attacker_gain)), target_user_id, Decimal(str(target_loss))
    )
    
    # 更新冷却时间和每日被指定次数
    await CooldownManager.update_cooldown(user_id, group_id, "ri")
    await CooldownManager.increment_daily_targeted(target_user_id, group_id)
    
    # 构建结果消息
    attacker_length_str = GameLogic.format_length(float(attacker_data.length))
    target_length_str = GameLogic.format_length(float(target_data.length))
    
    result_msg = UniMessage([
        "日群友成功！"
    ])
    
    if is_critical:
        result_msg.append("💥 暴击！")
    
    result_msg.extend([
        f"\n\n🔥 攻击者数据：\n",
        f"长度变化：{attacker_gain:+.2f}cm\n",
        f"当前长度：{attacker_length_str}\n\n",
        "😵 被攻击者数据：\n",
        target.result,
        f" 长度变化：{target_loss:+.2f}cm\n",
        target.result,
        f" 当前长度：{target_length_str}"
    ])
    
    await matcher.finish(result_msg)


# 排行榜命令（简单实现）
rank_alc = Alconna("/nndzz", Subcommand("rank"))
rank_alc.shortcut("牛牛排行榜", {"command": "/nndzz rank"})
rank_alc.shortcut("排行榜", {"command": "/nndzz rank"})

rank_cmd = on_alconna(
    rank_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)


@rank_cmd.assign("rank")
@handle_exceptions
async def handle_rank(matcher: AlconnaMatcher, event: GroupMessageEvent):
    """处理排行榜命令"""
    group_id = str(event.group_id)
    
    # 验证群组ID
    if not Validators.is_valid_group_id(group_id):
        await matcher.finish(ErrorMessages.INVALID_USER)
    
    # 获取排行榜数据
    leaderboard_data = await DatabaseService.get_leaderboard(group_id, limit=10)
    
    if not leaderboard_data:
        await matcher.finish("暂无排行榜数据")
    
    # 构建排行榜消息
    result_msg = "🏆 牛牛长度排行榜 🏆\n\n"
    
    for i, user_data in enumerate(leaderboard_data, 1):
        length_str = GameLogic.format_length(float(user_data.length))
        
        # 添加排名图标
        if i == 1:
            rank_icon = "🥇"
        elif i == 2:
            rank_icon = "🥈"
        elif i == 3:
            rank_icon = "🥉"
        else:
            rank_icon = f"{i}."
        
        result_msg += f"{rank_icon} {length_str}\n"
    
    await matcher.finish(result_msg)


# 重置命令（管理员功能）
reset_alc = Alconna("/nndzz", Subcommand("reset", Args["target?", At]))
reset_alc.shortcut("重置牛牛", {"command": "/nndzz reset"})

reset_cmd = on_alconna(
    reset_alc,
    rule=is_group_chat(),
    priority=10,
    block=True
)


@reset_cmd.assign("reset")
@handle_exceptions
async def handle_reset(matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]):
    """处理重置命令（仅限管理员）"""
    # 简单的权限检查（可以根据需要扩展）
    if event.sender.role not in ["admin", "owner"]:
        await matcher.finish("只有管理员才能使用重置功能")
    
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    
    if target.available:
        # 重置指定用户
        target_user_id = str(target.result.target)
        
        if not Validators.is_valid_user_id(target_user_id):
            await matcher.finish("目标用户信息无效")
        
        # 重置用户数据（设置长度为0）
        await DatabaseService.create_or_update_user_data(
            target_user_id, group_id, Decimal('0.00')
        )
        
        reply_msg = UniMessage([
            "已重置 ",
            target.result,
            " 的牛牛数据"
        ])
        await matcher.finish(reply_msg)
    else:
        # 重置自己
        await DatabaseService.create_or_update_user_data(
            user_id, group_id, Decimal('0.00')
        )
        await matcher.finish("已重置你的牛牛数据")
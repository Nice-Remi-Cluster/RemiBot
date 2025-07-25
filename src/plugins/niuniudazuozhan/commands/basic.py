"""基础命令处理模块"""

from decimal import Decimal
from typing import Optional

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import Rule
from nonebot_plugin_alconna import (
    Alconna,
    Subcommand,
    Args,
    AlconnaMatcher,
    Match,
    on_alconna,
)
from nonebot_plugin_alconna.uniseg import UniMessage, At

from ..models import OperationType
from ..services import DatabaseService, GameLogic, CooldownManager
from ..utils import Validators, handle_exceptions, ErrorMessages


def is_group_chat() -> Rule:
    """检查是否为群聊"""

    def _is_group(event: Event) -> bool:
        return isinstance(event, GroupMessageEvent)

    return Rule(_is_group)


# 导命令
dao_alc = Alconna("/nndzz", Subcommand("dao"))
# 添加中文快捷方式
dao_alc.shortcut("导", {"command": "/nndzz dao"})

dao_cmd = on_alconna(dao_alc, rule=is_group_chat(), priority=10, block=True)


@dao_cmd.assign("dao")
@handle_exceptions
async def handle_dao(matcher: AlconnaMatcher, event: GroupMessageEvent):
    """处理导命令"""
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    # 验证用户ID和群组ID
    if not Validators.is_valid_user_id(user_id) or not Validators.is_valid_group_id(
        group_id
    ):
        await matcher.finish(ErrorMessages.INVALID_USER)

    # 检查冷却时间
    can_use, remaining = await CooldownManager.check_cooldown(user_id, group_id, "dao")
    if not can_use:
        remaining_time = CooldownManager.format_remaining_time(remaining)
        await matcher.finish(f"牛牛还在休息中，请{remaining_time}后再试")

    # 执行导操作
    length_change = GameLogic.calculate_dao_change()

    # 检查是否暴击
    is_critical = GameLogic.is_critical_hit()
    if is_critical:
        length_change = GameLogic.apply_critical_multiplier(length_change, True)

    # 验证长度变化值
    if not Validators.validate_length_change(length_change):
        await matcher.finish(ErrorMessages.VALIDATION_ERROR)

    # 更新用户数据
    user_data = await DatabaseService.create_or_update_user_data(
        user_id, group_id, Decimal(str(length_change))
    )

    # 记录操作
    await DatabaseService.record_operation(
        user_id, group_id, OperationType.DAO, Decimal(str(length_change))
    )

    # 更新冷却时间
    await CooldownManager.update_cooldown(user_id, group_id, "dao")

    # 构建结果消息
    length_str = GameLogic.format_length(float(user_data.length))

    result_msg = f"导完了！"
    if is_critical:
        result_msg += "💥 暴击！"

    result_msg += f"\n长度变化：{length_change:+.2f}cm\n当前长度：{length_str}"

    await matcher.finish(result_msg)


# 查看命令
view_alc = Alconna("/nndzz", Subcommand("view", Args["target?", At]))
# 添加中文快捷方式
view_alc.shortcut("查看牛牛", {"command": "/nndzz view"})
view_alc.shortcut("查看", {"command": "/nndzz view"})
view_alc.shortcut("牛牛长度", {"command": "/nndzz view"})
# 支持带参数的中文快捷方式
view_alc.shortcut("查看牛牛 (.+)", {"command": "/nndzz view {0}"})

view_cmd = on_alconna(view_alc, rule=is_group_chat(), priority=10, block=True)


@view_cmd.assign("view")
@handle_exceptions
async def handle_view(
    matcher: AlconnaMatcher, event: GroupMessageEvent, target: Match[At]
):
    """处理查看命令"""
    group_id = str(event.group_id)

    # 验证群组ID
    if not Validators.is_valid_group_id(group_id):
        await matcher.finish(ErrorMessages.INVALID_USER)

    if target.available:
        # 查看指定用户（通过@）
        target_user_id = str(target.result.target)

        # 验证目标用户ID
        if not Validators.is_valid_user_id(target_user_id):
            await matcher.finish(ErrorMessages.INVALID_USER)

        user_data = await DatabaseService.get_user_data(target_user_id, group_id)
        if user_data is None:
            # 回复时 @ 目标用户
            reply_msg = UniMessage(
                [target.result, " 还没有牛牛数据，使用 '导' 命令开始游戏吧！"]
            )
            await matcher.finish(reply_msg)

        length_str = GameLogic.format_length(float(user_data.length))
        description = GameLogic.get_length_description(float(user_data.length))

        reply_msg = UniMessage(
            [
                target.result,
                f" 的牛牛数据：\n长度：{length_str}\n等级：{description}\n总操作次数：{user_data.total_operations}",
            ]
        )
        await matcher.finish(reply_msg)
    else:
        # 查看自己
        user_id = str(event.user_id)

        # 验证用户ID
        if not Validators.is_valid_user_id(user_id):
            await matcher.finish(ErrorMessages.INVALID_USER)

        user_data = await DatabaseService.get_user_data(user_id, group_id)
        if user_data is None:
            await matcher.finish("你还没有牛牛数据，使用 '导' 命令开始游戏吧！")

        length_str = GameLogic.format_length(float(user_data.length))

        result_msg = (
            f"你的牛牛数据：\n"
            f"长度：{length_str}\n"
            f"总操作次数：{user_data.total_operations}"
        )

        if user_data.last_operation_time:
            result_msg += f"\n最后操作：{user_data.last_operation_time.strftime('%Y-%m-%d %H:%M:%S')}"

        await matcher.finish(result_msg)


# 帮助命令
help_alc = Alconna("/nndzz", Subcommand("help"))
help_alc.shortcut("牛牛帮助", {"command": "/nndzz help"})
help_alc.shortcut("牛牛说明", {"command": "/nndzz help"})

help_cmd = on_alconna(help_alc, rule=is_group_chat(), priority=10, block=True)


@help_cmd.assign("help")
@handle_exceptions
async def handle_help(matcher: AlconnaMatcher, event: GroupMessageEvent):
    """处理帮助命令"""
    help_text = (
        "🐂 牛牛大作战 使用说明\n\n"
        "📝 基础命令：\n"
        "• 导 - 进行导操作，随机改变牛牛长度\n"
        "• 查看牛牛 - 查看自己的牛牛数据\n"
        "• 查看牛牛 @某人 - 查看指定用户的牛牛数据\n"
        "• 日群友 @某人 - 日指定群友（互动命令）\n"
        "• 牛牛排行榜 - 查看群内排行榜\n\n"
        "⏰ 冷却机制：\n"
        "• 导操作冷却：30分钟\n"
        "• 日群友冷却：60分钟\n"
        "• 每人每日最多被指定10次\n\n"
        "📊 数据说明：\n"
        "• 长度范围：-50cm ~ 100cm\n"
        "• 正数表示长度（cm），负数表示深度（cm深度）\n"
        "• 有10%概率触发暴击（1.5倍效果）\n\n"
        "💡 提示：所有数据按群组独立计算"
    )

    await matcher.finish(help_text)

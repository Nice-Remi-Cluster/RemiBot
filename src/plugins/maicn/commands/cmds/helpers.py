"""命令处理辅助函数

提供常用的用户绑定信息获取和验证功能，减少重复代码。
"""

from typing import Optional, Dict, Any
from nonebot import logger
from src.utils.helpers.remi_service_helper import RemiServiceHelper, UserBindType
from src.plugins.maicn.commands.matchers import maicn_matcher
from src.plugins.maicn.alias import alias_luoxue, alias_divingfish
from src.plugins.maicn.messages import Messages


async def get_user_bind_info_or_finish(
    user_qq: str, remi_helper: RemiServiceHelper
) -> Dict[str, Any]:
    """获取用户绑定信息，失败时直接结束对话

    Args:
        user_qq: 用户QQ号
        remi_helper: Remi服务助手实例

    Returns:
        用户绑定信息字典

    Raises:
        FinishedException: 当获取失败时直接结束对话
    """
    try:
        remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)
        if not remi_uuid:
            await maicn_matcher.finish(Messages.ERROR_SERVICE_UNAVAILABLE)

        user_current_maimai_bind = await remi_helper.get_current_maimai_bind_info(
            remi_uuid
        )
        if not user_current_maimai_bind:
            await maicn_matcher.finish(Messages.HINT_NO_MAIMAI_BIND)

        return user_current_maimai_bind

    except Exception as e:
        logger.exception(f"获取用户绑定信息失败: {e}")
        await maicn_matcher.finish(Messages.ERROR_SERVICE_UNAVAILABLE)


async def validate_bind_source(binds: Dict[str, Any], source: str) -> str:
    """验证并返回绑定的用户名

    Args:
        binds: 用户绑定信息
        source: 数据源名称

    Returns:
        绑定的用户名/好友码

    Raises:
        FinishedException: 当验证失败时直接结束对话
    """
    if not binds.get("others"):
        await maicn_matcher.finish(Messages.HINT_NO_BIND)

    # 查找对应的绑定信息
    bind_name = None
    target_bind_type = None

    if source in alias_luoxue:
        target_bind_type = UserBindType.Luoxue
        source_display = "落雪查分器"
    elif source in alias_divingfish:
        target_bind_type = UserBindType.DivingFish
        source_display = "水鱼查分器"
    else:
        await maicn_matcher.finish(Messages.ERROR_UNSUPPORTED_SOURCE)

    for bind in binds["others"]:
        if bind["bind_type"] == target_bind_type:
            if target_bind_type == UserBindType.DivingFish:
                # 水鱼查分器需要解析JSON格式的账号密码
                try:
                    import json

                    bind_data = json.loads(bind["bind_content"])
                    bind_name = bind_data["username"]  # 返回用户名用于显示
                except (json.JSONDecodeError, KeyError):
                    await maicn_matcher.finish(Messages.ERROR_SHUIYU_BIND_FORMAT)
            else:
                # 落雪查分器直接使用bind_content
                bind_name = bind["bind_content"]
            break

    if not bind_name:
        if target_bind_type == UserBindType.Luoxue:
            await maicn_matcher.finish(Messages.HINT_NO_LXNS_BIND)
        else:
            await maicn_matcher.finish(Messages.HINT_NO_SHUIYU_BIND)

    return bind_name


async def get_divingfish_credentials(binds: Dict[str, Any]) -> tuple[str, str]:
    """获取水鱼查分器的账号密码

    Args:
        binds: 用户绑定信息

    Returns:
        (username, password) 元组

    Raises:
        FinishedException: 当解析失败时直接结束对话
    """
    df_bind = None
    for bind in binds.get("others", []):
        if bind["bind_type"] == UserBindType.DivingFish:
            df_bind = bind
            break

    if not df_bind:
        await maicn_matcher.finish(Messages.HINT_NO_SHUIYU_BIND)

    try:
        import json

        bind_data = json.loads(df_bind["bind_content"])
        username = bind_data["username"]
        password = bind_data["password"]
        return username, password
    except json.JSONDecodeError:
        logger.error(f"水鱼绑定数据格式错误: {df_bind['bind_content']}")
        await maicn_matcher.finish(Messages.ERROR_SHUIYU_BIND_FORMAT)
    except KeyError as e:
        logger.error(f"水鱼绑定数据缺少必要字段: {e}")
        await maicn_matcher.finish(Messages.ERROR_SHUIYU_BIND_FORMAT)


async def get_remi_uuid_or_finish(user_qq: str, remi_helper: RemiServiceHelper) -> str:
    """获取用户UUID，失败时直接结束对话

    Args:
        user_qq: 用户QQ号
        remi_helper: Remi服务助手实例

    Returns:
        用户UUID

    Raises:
        FinishedException: 当获取失败时直接结束对话
    """
    try:
        remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)
        if not remi_uuid:
            await maicn_matcher.finish(Messages.ERROR_SERVICE_UNAVAILABLE)
        return remi_uuid
    except Exception as e:
        logger.exception(f"获取用户UUID失败: {e}")
        await maicn_matcher.finish(Messages.ERROR_SERVICE_UNAVAILABLE)

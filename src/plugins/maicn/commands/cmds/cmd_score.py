import httpx
from nonebot import logger
from maimai_py import PlayerIdentifier
from nonebot import get_plugin_config
from arclet.alconna import SubcommandResult
from nonebot import require
from nonebot.exception import FinishedException

from src.plugins.maicn.alias import alias_luoxue, alias_divingfish
from src.plugins.maicn.libraries import (
    maimai_py_client,
    lxns_provider,
    get_maimai_user_all_score,
    mai_cn_score_to_maimaipy,
    divingfish_provider,
    get_maimai_user_preview_info,
    B50ImageGenerator,
)
from nonebot.adapters.onebot.v11.event import MessageEvent
from src.utils.helpers.remi_service_helper import RemiServiceHelper, UserBindType

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Query as AlcQuery, UniMessage

from src.plugins.maicn.config import Config

from src.plugins.maicn.commands.matchers import maicn_matcher
from src.plugins.maicn.commands.cmds.helpers import (
    get_user_bind_info_or_finish,
    validate_bind_source,
    get_divingfish_credentials,
)
from src.plugins.maicn.messages import Messages
from src.plugins.permission_manager import require_permission

config = get_plugin_config(Config)


@maicn_matcher.assign("update")
@require_permission("maicn", "update")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("update", 0)):
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()
    update_source = r.args.get("source") or None
    remi_helper = RemiServiceHelper(config.remi_service_base_url)

    # 使用辅助函数获取用户绑定信息
    user_current_maimai_bind = await get_user_bind_info_or_finish(user_qq, remi_helper)
    maimai_uid = user_current_maimai_bind["maimai"]["bind_content"]

    if not user_current_maimai_bind["others"]:
        await maicn_matcher.finish(Messages.HINT_NO_BIND)

    source_updated = []
    user_score = await mai_cn_score_to_maimaipy(
        await get_maimai_user_all_score(maimai_uid)
    )

    if not update_source or update_source in alias_divingfish:
        df_bind = None
        for bind in user_current_maimai_bind["others"]:
            if bind["bind_type"] == UserBindType.DivingFish:
                df_bind = bind
                break
        if df_bind:
            try:
                username, password = await get_divingfish_credentials(
                    user_current_maimai_bind
                )
                await maimai_py_client.updates(
                    identifier=PlayerIdentifier(
                        username=username, credentials=password
                    ),
                    scores=user_score,
                    provider=divingfish_provider,
                )
                source_updated.append("水鱼")
            except Exception as e:
                logger.exception(f"更新水鱼数据失败: {e}")
                await maicn_matcher.finish(Messages.ERROR_SHUIYU_UPDATE_FAILED)

    if not update_source or update_source in alias_luoxue:
        lx_bind = None
        for bind in user_current_maimai_bind["others"]:
            if bind["bind_type"] == UserBindType.Luoxue:
                lx_bind = bind
                break
        if lx_bind:
            try:
                await maimai_py_client.updates(
                    identifier=PlayerIdentifier(friend_code=lx_bind["bind_content"]),
                    scores=user_score,
                    provider=lxns_provider,
                )
            except httpx.HTTPStatusError as e:
                if "404 Not Found" in str(e):
                    await maicn_matcher.finish(Messages.ERROR_LXNS_USER_NOT_FOUND)
                else:
                    logger.exception(f"落雪API请求失败: {e}")
                    await maicn_matcher.finish(Messages.ERROR_LXNS_UPDATE_FAILED)
            except Exception as e:
                logger.exception(f"更新落雪数据失败: {e}")
                await maicn_matcher.finish(Messages.ERROR_LXNS_UPDATE_FAILED)

            source_updated.append("落雪")

    if source_updated:
        await maicn_matcher.finish(
            Messages.format_score_update_success(",".join(source_updated))
        )
    else:
        await maicn_matcher.finish(Messages.ERROR_NO_UPDATE_SOURCE)


@maicn_matcher.assign("b50")
@require_permission("maicn", "b50")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("b50", 0)):
    """处理b50命令"""
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()
    source = r.args.get("source") or "落雪"

    try:
        # 获取用户绑定信息
        remi_helper = RemiServiceHelper(config.remi_service_base_url)
        user_current_maimai_bind = await get_user_bind_info_or_finish(
            user_qq, remi_helper
        )

        # 获取玩家基本信息
        mai_uid = int(user_current_maimai_bind["maimai"]["bind_content"])
        player_preview = await get_maimai_user_preview_info(mai_uid)

        # 选择数据源
        provider = lxns_provider if source in alias_luoxue else divingfish_provider

        # 获取绑定的查分器用户名
        bind_name = await validate_bind_source(user_current_maimai_bind, source)

        # 使用maimai_py获取B50数据
        if source in alias_luoxue:
            # 落雪查分器使用friend_code
            player_identifier = PlayerIdentifier(friend_code=bind_name)
        else:
            # 水鱼查分器使用账号密码
            username, password = await get_divingfish_credentials(
                user_current_maimai_bind
            )
            player_identifier = PlayerIdentifier(
                username=username, credentials=password
            )

        player_scores = await maimai_py_client.scores(
            player_identifier, provider=provider
        )

        if not player_scores:
            await maicn_matcher.finish(Messages.ERROR_SCORE_DATA_FETCH_FAILED)

        # 获取B35和B15数据
        b35_scores = player_scores.scores_b35
        b15_scores = player_scores.scores_b15

        # 生成图片
        generator = B50ImageGenerator()

        # 转换数据格式
        b35_data = [generator._convert_score_to_dict(score) for score in b35_scores]
        b15_data = [generator._convert_score_to_dict(score) for score in b15_scores]

        # 准备玩家数据
        player_data = {
            "name": player_preview.get("userName", "Unknown"),
            "rating": player_scores.rating,
        }

        image_bytes = generator.generate_b50_image(player_data, b35_data, b15_data)

        # 发送图片
        message = UniMessage.image(raw=image_bytes)

        await maicn_matcher.finish(message)

    except FinishedException as e:
        raise e

    except Exception as e:
        logger.exception(f"B50命令执行失败: {e}")
        await maicn_matcher.finish(Messages.ERROR_B50_GENERATE_FAILED)

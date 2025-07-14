import httpx
from loguru import logger
from maimai_py import PlayerIdentifier
from nonebot import get_plugin_config
from arclet.alconna import SubcommandResult
from nonebot import require

from src.plugins.maimaidx.plugins.maicn.alias import alias_luoxue, alias_divingfish
from src.plugins.maimaidx.libraries.maimai_cn import maimai_py_client, lxns_provider, get_maimai_user_all_score, \
    mai_cn_score_to_maimaipy, divingfish_provider
from nonebot.adapters.onebot.v11.event import MessageEvent
from src.utils.helpers.remi_service_helper import RemiServiceHelper, UserBindType

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Query as AlcQuery

from src.plugins.maimaidx.plugins.maicn.config import Config

from src.plugins.maimaidx.plugins.maicn.commands.matchers import maicn_matcher

config = get_plugin_config(Config)


@maicn_matcher.assign("update")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("update", 0)):
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()
    update_source = r.args.get("source") or None
    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)
    user_current_maimai_bind = await remi_helper.get_current_maimai_bind_info(remi_uuid)

    maimai_uid = user_current_maimai_bind["maimai"]["bind_content"]

    if not user_current_maimai_bind["others"]:
        await maicn_matcher.finish("该账号未绑定任何查分器")

    source_updated = []
    user_score = await mai_cn_score_to_maimaipy(await get_maimai_user_all_score(maimai_uid))

    if not update_source or update_source in alias_divingfish:
        df_bind = None
        for bind in user_current_maimai_bind["others"]:
            if bind["bind_type"] == UserBindType.DivingFish:
                df_bind = bind
                break
        if df_bind:
            try:
                await maimai_py_client.updates(
                    identifier=PlayerIdentifier(credentials=df_bind["bind_content"]),
                    scores=user_score,
                    provider=divingfish_provider
                )
            except Exception as e:
                logger.exception(e)
                await maicn_matcher.finish(f"更新水鱼数据失败，Error: {e}")
            source_updated.append("水鱼")

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
                    provider=lxns_provider
                )
            except httpx.HTTPStatusError as e:
                if "404 Not Found" in e.args[0]:
                    await maicn_matcher.finish(f"用户绑定的好友码在落雪没有档案")
            except Exception as e:
                logger.exception(e)
                await maicn_matcher.finish(f"更新落雪数据失败，Error: {e}")

            source_updated.append("落雪")

    await maicn_matcher.finish(f"已更新{','.join(source_updated)}的数据")

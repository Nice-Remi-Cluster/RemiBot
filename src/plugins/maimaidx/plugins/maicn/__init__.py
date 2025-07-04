from loguru import logger
from maimai_py import PlayerIdentifier
from nonebot import get_plugin_config
from arclet.alconna import Alconna, Subcommand, SubcommandResult
from nonebot import require
from nonebot.plugin import PluginMetadata
from wahlap_mai_ass_expander.exceptions import QrCodeExpired, QrCodeInvalid

from .alias import alias_luoxue, alias_divingfish
from .maimai_cn_helper import maimai_py_client, divingfish_provider, lxns_provider, get_maimai_user_all_score, \
    mai_cn_score_to_maimaipy, get_maimai_user_preview_info
from src.utils.helpers.alconna_helper import alc_header, alc_header_cn
from nonebot.adapters.onebot.v11.event import MessageEvent
from httpx import AsyncClient
from .enums import UserBindType
from .maimai_cn_helper import get_maimai_uid
from src.utils.helpers.remi_service_helper import RemiServiceHelper
from .alconna import maicn_alc, lx_alc

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Args, on_alconna, AlconnaResult, CommandResult, Query as AlcQuery

from .config import Config

config = get_plugin_config(Config)

maicn_matcher = on_alconna(maicn_alc)
lx_matcher = on_alconna(lx_alc)

@maicn_matcher.assign("add.sgwcmaid")
async def _(
        event: MessageEvent,
        alc_result: AlcQuery = AlcQuery("add", 0)
):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    sgwcmaid = r.args["sgwcmaid"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)

    try:
        mai_uid = await get_maimai_uid(sgwcmaid)
    except QrCodeExpired:
        await maicn_matcher.finish("二维码已过期")
    except QrCodeInvalid:
        await maicn_matcher.finish("二维码无效")
    except Exception as e:
        logger.exception(e)
        await maicn_matcher.finish(f"添加失败，Error: {e}")

    remi_uuid = await remi_service_helper.get_uuid_or_create_by_qq(user_qq)
    if not remi_uuid:
        await maicn_matcher.finish("获取用户uuid失败，请联系管理员")

    if not await remi_service_helper.user_add_bind(remi_uuid, UserBindType.MaimaiCN, mai_uid, bind_name):
        await maicn_matcher.finish("添加失败，请联系管理员查看日志")

    await maicn_matcher.finish("添加乌蒙账号成功")

@maicn_matcher.assign("bind.source.bind_name")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("bind", 0)):
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()

    source: str = r.args["source"]
    bind_name = r.args["bind_name"]

    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)

    param = ""
    if source in alias_divingfish:
        param = "divingfish_bind_name"
    elif source in alias_luoxue:
        param = "luoxue_bind_name"

    if not param:
        return await maicn_matcher.finish("未找到绑定源")

    binds = await remi_helper.update_current_maimai_bind(
        **{
            "uuid": remi_uuid,
            param: bind_name,
        }
    )
    if not binds:
        return await maicn_matcher.finish("更新绑定失败")

    mai_preview_info = await get_maimai_user_preview_info(int(binds["maimai"]["bind_content"]))
    return await maicn_matcher.finish(
        f"更新绑定成功, 新的绑定信息如下\n"
        f"=============\n"
        f"MaimaiDX:\n"
        f"{mai_preview_info['userName']}\n"
        f"Rating: {mai_preview_info['playerRating']}\n"
        f"-------------\n"
        f"档案绑定信息:\n"
        f"{binds['others']}"
    )

    # if source in alias_divingfish:
    #     binds = await remi_helper.update_current_maimai_bind(
    #         remi_uuid,
    #         divingfish_bind_name=bind_name
    #     )
    #     if not binds:
    #         return await maicn_matcher.finish("更新绑定失败")
    #     return await maicn_matcher.finish(
    #         f"更新绑定成功, 新的绑定信息如下\n"
    #     )
    # elif source in alias_luoxue:
    #     binds = await remi_helper.update_current_maimai_bind(
    #         remi_uuid,
    #         luoxue_bind_name=bind_name
    #     )
    #     if not binds:
    #         return await maicn_matcher.finish("更新绑定失败")
    #     return await maicn_matcher.finish(
    #         f"更新绑定成功, 新的绑定信息如下\n"
    #     )
    #
    # return await maicn_matcher.finish("未找到绑定源")


@maicn_matcher.assign("update")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("update", 0)):
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()
    update_source = r.args.get("source") or None
    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)
    user_current_maimai_bind = await remi_helper.get_current_maimai_bind_info(remi_uuid)

    maimai_uid = user_current_maimai_bind["maimai"]["bind_content"]

    source_updated = []
    if not update_source or update_source in alias_divingfish:
        pass

    if not update_source or update_source in alias_luoxue:
        lx_bind = None
        for bind in user_current_maimai_bind["others"]:
            if bind["bind_type"] == UserBindType.Luoxue:
                lx_bind = bind
                break
        if lx_bind:
            friend_code = lx_bind["bind_content"]

            user_score = await mai_cn_score_to_maimaipy(await get_maimai_user_all_score(maimai_uid))
            await maimai_py_client.updates(
                identifier=PlayerIdentifier(friend_code=friend_code),
                scores=user_score,
                provider=lxns_provider
            )
            source_updated.append("落雪")

    await maicn_matcher.finish(f"已更新{','.join(source_updated)}的数据")

@maicn_matcher.assign("current.profile")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("current", 0)):
    r: SubcommandResult = alc_result.result
    profile = r.args.get("profile")
    user_qq = event.get_user_id()
    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)

    result = await remi_helper.switch_current_maimai_bind(remi_uuid, profile)
    if not result:
        await maicn_matcher.finish("切换失败，可能是没有此档案或其他原因")

    mai_bind = result["maimai"]
    mai_preview_info = await get_maimai_user_preview_info(int(mai_bind["bind_content"]))
    await maicn_matcher.finish(
        f"切换到maimai档案:\n"
        f"=============\n"
        f"MaimaiDX:\n"
        f"{mai_preview_info['userName']}\n"
        f"Rating: {mai_preview_info['playerRating']}\n"
        f"-------------\n"
        f"档案绑定信息:\n"
        f"{result['others']}"
    )

@maicn_matcher.assign("current")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("current", 0)):
    r: SubcommandResult = alc_result.result

    remi_helper = RemiServiceHelper(config.remi_service_base_url)

    user_qq = event.get_user_id()

    remi_uuid = await remi_helper.get_uuid_or_create_by_qq(user_qq)

    current_maimai_binds = await remi_helper.get_current_maimai_bind_info(remi_uuid)

    if not current_maimai_binds:
        await maicn_matcher.finish("未绑定任何乌蒙账号")

    mai_bind = current_maimai_binds["maimai"]
    mai_preview_info = await get_maimai_user_preview_info(int(mai_bind["bind_content"]))
    await maicn_matcher.finish(
        f"当前使用的maimaidx档案如下:\n"
        f"=============\n"
        f"MaimaiDX:\n"
        f"{mai_preview_info['userName']}\n"
        f"Rating: {mai_preview_info['playerRating']}\n"
        f"-------------\n"
        f"档案绑定信息:\n"
        f"{current_maimai_binds['others']}"
    )


@lx_matcher.assign("add.friend_code")
async def _(
        event: MessageEvent,
        alc_result: AlcQuery = AlcQuery("add", 0)
):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    friend_code = r.args["friend_code"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)

    remi_uuid = await remi_service_helper.get_uuid_or_create_by_qq(user_qq)
    if not remi_uuid:
        await maicn_matcher.finish("获取用户uuid失败，请联系管理员")

    if not await remi_service_helper.user_add_bind(remi_uuid, UserBindType.Luoxue, friend_code, bind_name):
        await maicn_matcher.finish("添加失败，请联系管理员查看日志")

    await maicn_matcher.finish("添加落雪查分器成功")
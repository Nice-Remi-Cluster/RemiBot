import json

from loguru import logger
from nonebot import get_plugin_config
from arclet.alconna import SubcommandResult
from nonebot import require
from wahlap_mai_ass_expander.exceptions import QrCodeExpired, QrCodeInvalid

from src.plugins.maimaidx.libraries.lxns import LXNSClient
from src.plugins.maimaidx.plugins.maicn.alias import alias_luoxue, alias_divingfish
from src.plugins.maimaidx.libraries.maimai_cn import get_maimai_user_preview_info
from nonebot.adapters.onebot.v11.event import MessageEvent
from src.plugins.maimaidx.libraries.maimai_cn import get_maimai_uid
from src.utils.helpers.remi_service_helper import RemiServiceHelper, UserBindType, MaimaiBindInfo

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Query as AlcQuery

from src.plugins.maimaidx.plugins.maicn.config import Config

from src.plugins.maimaidx.plugins.maicn.commands.matchers import maicn_matcher, lx_matcher, divingfish_matcher

config = get_plugin_config(Config)


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

    remi_uuid = await remi_service_helper.get_uuid_or_create_by_qq(user_qq)
    if not remi_uuid:
        await maicn_matcher.finish("获取用户uuid失败，请联系管理员")

    mai_uid = 0
    try:
        mai_uid = await get_maimai_uid(sgwcmaid)
    except QrCodeExpired:
        await maicn_matcher.finish("二维码已过期")
    except QrCodeInvalid:
        await maicn_matcher.finish("二维码无效")
    except Exception as e:
        logger.exception(e)
        await maicn_matcher.finish(f"添加失败，Error: {e}")

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


@lx_matcher.assign("create")
async def _(
        event: MessageEvent,
        alc_result: AlcQuery = AlcQuery("create", 0)
):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)
    lx_client = LXNSClient()

    remi_uuid = await remi_service_helper.get_uuid_or_create_by_qq(user_qq)
    if not remi_uuid:
        await maicn_matcher.finish("获取用户uuid失败，请联系管理员")

    current_bind = await remi_service_helper.get_current_maimai_bind_info(remi_uuid)
    if not current_bind:
        await maicn_matcher.finish("未绑定任何乌蒙账号")

    current_bind: MaimaiBindInfo
    lx_bind = None
    for bind in current_bind["others"]:
        if bind["bind_type"] == UserBindType.Luoxue:
            lx_bind = bind
            break
    if not lx_bind:
        await maicn_matcher.finish("当前maimai档案未绑定落雪查分器")

    friend_code = lx_bind["bind_content"]

    if info := await lx_client.maimai_player(friend_code):
        # info_formatted = json.dumps(info, ensure_ascii=False, indent=4, separators=(',', ': '))
        await lx_matcher.finish(f"该档案绑定的好友码已经有了对应的档案(\n{info['name']})")

    mai_uid = current_bind["maimai"]["bind_content"]
    mai_preview_info = await get_maimai_user_preview_info(int(mai_uid))
    mai_user_name = mai_preview_info["userName"]


    player_data = {
        "name": mai_user_name,
        "rating": 0,
        "friend_code": int(friend_code),
        "course_rank": 0,
        "class_rank": 0,
        "star": 0,
        "trophy_name": "新人出道",
        "icon": {
            "id": 1
        },
        "name_plate": {
            "id": 1
        },
        "frame": {
            "id": 1
        }
    }

    if await lx_client.update_maimai_player(player_data):
        player_info = await lx_client.maimai_player(friend_code)
        player_info_formatted = json.dumps(player_info, ensure_ascii=False, indent=4, separators=(',', ': '))
        await lx_matcher.finish(f"创建落雪档案成功，档案内容如下:\n{player_info_formatted}")
    else:
        await lx_matcher.finish("创建落雪档案失败")


@divingfish_matcher.assign("add.import_token")
async def _(
        event: MessageEvent,
        alc_result: AlcQuery = AlcQuery("add", 0)
):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    import_token = r.args["import_token"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)

    remi_uuid = await remi_service_helper.get_uuid_or_create_by_qq(user_qq)
    if not remi_uuid:
        await maicn_matcher.finish("获取用户uuid失败，请联系管理员")

    if not await remi_service_helper.user_add_bind(remi_uuid, UserBindType.DivingFish, import_token, bind_name):
        await maicn_matcher.finish("添加失败，请联系管理员查看日志")

    await maicn_matcher.finish("添加水鱼查分器成功")

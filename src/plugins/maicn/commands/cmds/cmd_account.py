import json

from nonebot import logger
from nonebot import get_plugin_config
from arclet.alconna import SubcommandResult
from nonebot import require
from wahlap_mai_ass_expander.exceptions import QrCodeExpired, QrCodeInvalid

from src.plugins.maicn.libraries.lxns import LXNSClient
from src.plugins.maicn.alias import alias_luoxue, alias_divingfish
from src.plugins.maicn.libraries import get_maimai_user_preview_info
from nonebot.adapters.onebot.v11.event import MessageEvent
from src.plugins.maicn.libraries import get_maimai_uid
from src.utils.helpers.remi_service_helper import (
    RemiServiceHelper,
    UserBindType,
    MaimaiBindInfo,
)
from src.plugins.maicn.messages import Messages

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Query as AlcQuery

from src.plugins.maicn.config import Config

from src.plugins.maicn.commands.matchers import (
    maicn_matcher,
    lx_matcher,
    divingfish_matcher,
)
from src.plugins.maicn.commands.cmds.helpers import (
    get_remi_uuid_or_finish,
)
from src.plugins.permission_manager import require_permission

config = get_plugin_config(Config)


@maicn_matcher.assign("add.sgwcmaid")
@require_permission("maicn", "add")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("add", 0)):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    sgwcmaid = r.args["sgwcmaid"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_service_helper)

    mai_uid = 0
    try:
        mai_uid = await get_maimai_uid(sgwcmaid)
    except QrCodeExpired:
        await maicn_matcher.finish(Messages.ERROR_QR_EXPIRED)
    except QrCodeInvalid:
        await maicn_matcher.finish(Messages.ERROR_QR_INVALID)
    except Exception as e:
        logger.exception(f"获取maimai UID失败: {e}")
        await maicn_matcher.finish(Messages.ERROR_ADD_FAILED)

    if not await remi_service_helper.user_add_bind(
        remi_uuid, UserBindType.MaimaiCN, mai_uid, bind_name
    ):
        await maicn_matcher.finish(Messages.ERROR_ADD_FAILED)

    await maicn_matcher.finish(Messages.SUCCESS_MAIMAI_ADDED)


@maicn_matcher.assign("bind.source.bind_name")
@require_permission("maicn", "bind")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("bind", 0)):
    r: SubcommandResult = alc_result.result
    user_qq = event.get_user_id()

    source: str = r.args["source"]
    bind_name = r.args["bind_name"]

    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_helper)

    param = ""
    if source in alias_divingfish:
        param = "divingfish_bind_name"
    elif source in alias_luoxue:
        param = "luoxue_bind_name"

    if not param:
        return await maicn_matcher.finish(Messages.ERROR_BIND_SOURCE_NOT_FOUND)

    binds = await remi_helper.update_current_maimai_bind(
        **{
            "uuid": remi_uuid,
            param: bind_name,
        }
    )
    if not binds:
        return await maicn_matcher.finish(Messages.ERROR_UPDATE_FAILED)

    mai_preview_info = await get_maimai_user_preview_info(
        int(binds["maimai"]["bind_content"])
    )
    return await maicn_matcher.finish(
        Messages.format_bind_update_success(
            mai_preview_info["userName"],
            mai_preview_info["playerRating"],
            binds["others"],
        )
    )


@maicn_matcher.assign("current.profile")
@require_permission("maicn", "current")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("current", 0)):
    r: SubcommandResult = alc_result.result
    profile = r.args.get("profile")
    user_qq = event.get_user_id()
    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_helper)

    result = await remi_helper.switch_current_maimai_bind(remi_uuid, profile)
    if not result:
        await maicn_matcher.finish(Messages.ERROR_SWITCH_FAILED)

    mai_bind = result["maimai"]
    mai_preview_info = await get_maimai_user_preview_info(int(mai_bind["bind_content"]))
    await maicn_matcher.finish(
        Messages.format_profile_switch_success(
            mai_preview_info["userName"],
            mai_preview_info["playerRating"],
            result["others"],
        )
    )


@maicn_matcher.assign("current")
@require_permission("maicn", "current")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("current", 0)):
    r: SubcommandResult = alc_result.result

    remi_helper = RemiServiceHelper(config.remi_service_base_url)
    user_qq = event.get_user_id()
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_helper)

    current_maimai_binds = await remi_helper.get_current_maimai_bind_info(remi_uuid)

    if not current_maimai_binds:
        await maicn_matcher.finish(Messages.HINT_NO_MAIMAI_BIND)

    mai_bind = current_maimai_binds["maimai"]
    mai_preview_info = await get_maimai_user_preview_info(int(mai_bind["bind_content"]))
    await maicn_matcher.finish(
        Messages.format_current_profile(
            mai_preview_info["userName"],
            mai_preview_info["playerRating"],
            current_maimai_binds["others"],
        )
    )


@lx_matcher.assign("add.friend_code")
@require_permission("lxns", "add")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("add", 0)):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    friend_code = r.args["friend_code"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_service_helper)

    if not await remi_service_helper.user_add_bind(
        remi_uuid, UserBindType.Luoxue, friend_code, bind_name
    ):
        await maicn_matcher.finish(Messages.ERROR_ADD_FAILED)

    await maicn_matcher.finish(Messages.SUCCESS_LXNS_ADDED)


@lx_matcher.assign("create")
@require_permission("lxns", "create")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("create", 0)):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)
    lx_client = LXNSClient()
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_service_helper)

    current_bind = await remi_service_helper.get_current_maimai_bind_info(remi_uuid)
    if not current_bind:
        await maicn_matcher.finish(Messages.HINT_NO_MAIMAI_BIND)

    current_bind: MaimaiBindInfo
    lx_bind = None
    for bind in current_bind["others"]:
        if bind["bind_type"] == UserBindType.Luoxue:
            lx_bind = bind
            break
    if not lx_bind:
        await maicn_matcher.finish(Messages.HINT_NO_LXNS_BIND)

    friend_code = lx_bind["bind_content"]

    if info := await lx_client.maimai_player(friend_code):
        await lx_matcher.finish(Messages.format_lxns_profile_exists(info["name"]))

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
        "icon": {"id": 1},
        "name_plate": {"id": 1},
        "frame": {"id": 1},
    }

    if await lx_client.update_maimai_player(player_data):
        player_info = await lx_client.maimai_player(friend_code)
        player_info_formatted = json.dumps(
            player_info, ensure_ascii=False, indent=4, separators=(",", ": ")
        )
        await lx_matcher.finish(
            Messages.format_lxns_create_success_with_info(player_info_formatted)
        )
    else:
        await lx_matcher.finish(Messages.ERROR_CREATE_LXNS_FAILED)


@divingfish_matcher.assign("add.username.password")
@require_permission("divingfish", "add")
async def _(event: MessageEvent, alc_result: AlcQuery = AlcQuery("add", 0)):
    r: SubcommandResult = alc_result.result

    user_qq = event.get_user_id()
    username = r.args["username"]
    password = r.args["password"]
    bind_name = r.args.get("bind_name", None)

    remi_service_helper = RemiServiceHelper(config.remi_service_base_url)
    remi_uuid = await get_remi_uuid_or_finish(user_qq, remi_service_helper)

    # 使用新的专用水鱼绑定API
    if not await remi_service_helper.user_add_divingfish_bind(
        remi_uuid, username, password, bind_name
    ):
        await maicn_matcher.finish(Messages.ERROR_ADD_FAILED)

    await maicn_matcher.finish(Messages.SUCCESS_SHUIYU_ADDED)

import httpx
from nonebot import logger
from nonebot import get_plugin_config

from src.plugins.maicn.config import Config

config = get_plugin_config(Config)


class LXNSClient:
    _client: httpx.AsyncClient

    def __init__(self, httpx_client: httpx.AsyncClient = None):
        if (
            httpx_client
            and httpx_client.base_url == config.lxns_base_url
            and httpx_client.headers.get("Authorization") == config.lxns_developer_token
        ):
            self._client = httpx_client
        else:
            self._client = httpx.AsyncClient(
                base_url=config.lxns_base_url,
                headers={"Authorization": config.lxns_developer_token},
            )

    async def maimai_player(self, friend_code: str | int) -> dict | None:
        """
        获取玩家信息
        """
        resp = await self._client.get(f"/api/v0/maimai/player/{friend_code}")

        if (
            resp.status_code == 200
            and resp.json()["success"] is True
            and resp.json()["code"] == 200
        ):
            return resp.json()["data"]
        return None

    async def update_maimai_player(self, player: dict) -> bool:
        """
        创建或修改玩家信息
        """
        resp = await self._client.post("/api/v0/maimai/player", json=player)

        logger.debug(
            f"LXNSClient-update_maimai_player: \n"
            f"url: {resp.request.url}\n"
            f"req_headers: {resp.request.headers}\n"
            f"method: {resp.request.method}\n"
            f"resp:{resp.json()}"
        )

        return bool(resp.status_code == 200 and resp.json()["success"] is True and resp.json()["code"] == 200)

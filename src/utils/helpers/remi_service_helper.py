from enum import StrEnum
from typing import TypedDict

from httpx import AsyncClient


class UserBindType(StrEnum):
    """
    用户绑定类型枚举
    """

    QQ = "qq"
    DivingFish = "divingfish"
    Luoxue = "luoxue"
    MaimaiCN = "maimai_cn"


class _V1UserCreateByQQResponse(TypedDict):
    uuid: str
    qq: str
    created_at: str


class _V1UserAddBindResponse(TypedDict):
    uuid: str
    bind_type: UserBindType
    bind_content: str
    bind_name: str
    is_default: bool


class V1MaimaiGetCurrentMaimaiBindResponseSingle(TypedDict):
    bind_type: UserBindType
    bind_content: str
    bind_name: str
    is_default: bool


class MaimaiBindInfo(TypedDict):
    """
    maimai绑定信息
    """

    maimai: V1MaimaiGetCurrentMaimaiBindResponseSingle
    others: list[V1MaimaiGetCurrentMaimaiBindResponseSingle]


class RemiServiceHelper:
    def __init__(self, base_url: str):
        self._client = AsyncClient(base_url=base_url)

    async def user_create_by_qq(self, qq: str) -> _V1UserCreateByQQResponse | None:
        resp = await self._client.post("/v1/user/create-by-qq", json={"qq": qq})

        if resp.status_code == 201:
            return resp.json()

        return None

    async def user_get_uuid(
        self, bind_type: UserBindType, bind_content: str
    ) -> str | None:
        """
        通过bind内容获取用户的uuid

        Args:
            bind_type: 绑定类型，可选值包括 qq, divingfish, luoxue, maimai_cn
            bind_content: 绑定内容

        Returns:
            成功返回响应uuid
        """
        resp = await self._client.get(
            "/v1/user/get-uuid",
            params={"bind_type": bind_type, "bind_content": bind_content},
        )

        match resp.status_code:
            case 200:
                return resp.json()["uuid"]
            case 404:
                return None

        return None

    async def user_add_bind(
        self,
        uuid: str,
        bind_type: UserBindType,
        bind_content: str,
        bind_name: str = None,
    ) -> _V1UserAddBindResponse | None:
        """
        添加一个新的用户账户绑定关系

        Args:
            uuid: 用户的uuid
            bind_type: 绑定类型，可选值包括qq, divingfish, luoxue, maimai_cn
            bind_content: 绑定内容
            bind_name: 绑定名称（可选）

        Returns:
            成功返回响应JSON，失败返回None
        """
        params = {"uuid": uuid, "bind_type": bind_type, "bind_content": bind_content}

        if bind_name:
            params["bind_name"] = bind_name

        resp = await self._client.get("/v1/user/add-bind", params=params)

        if resp.status_code == 200:
            return resp.json()

        return None

    async def user_add_divingfish_bind(
        self,
        uuid: str,
        username: str,
        password: str,
        bind_name: str = None,
    ) -> _V1UserAddBindResponse | None:
        """
        添加水鱼查分器绑定（账号密码方式）

        Args:
            uuid: 用户的uuid
            username: 水鱼账号用户名
            password: 水鱼账号密码
            bind_name: 绑定名称（可选，默认使用用户名）

        Returns:
            成功返回响应JSON，失败返回None
        """
        data = {
            "username": username,
            "password": password
        }
        
        if bind_name:
            data["bind_name"] = bind_name

        resp = await self._client.post(
            "/v1/user/add-divingfish-bind",
            params={"uuid": uuid},
            json=data
        )

        if resp.status_code == 200:
            return resp.json()

        return None

    async def user_get_binds(
        self, uuid: str, bind_type: UserBindType, default: bool = False
    ) -> list[_V1UserAddBindResponse] | None:
        """
        获取指定类型的所有绑定关系

        Args:
            uuid: 用户的uuid
            bind_type: 绑定类型
            default: 仅获取默认绑定

        Returns:
            成功返回包含绑定关系的列表，失败返回None
        """
        resp = await self._client.get(
            "/v1/user/get-binds",
            params={"uuid": uuid, "bind_type": bind_type, "default": default},
        )

        if resp.status_code == 200:
            return resp.json()

        return None

    async def get_uuid_or_create_by_qq(self, qq: str) -> str | None:
        """
        通过QQ获取用户UUID，如果用户不存在则创建一个新用户

        Args:
            qq: 用户的QQ号

        Returns:
            成功返回包含uuid的字典，失败返回None
        """
        # 首先尝试获取用户UUID
        result = await self.user_get_uuid(UserBindType.QQ, qq)

        # 如果用户存在，直接返回结果
        if result is not None:
            return result

        # 如果用户不存在，创建新用户
        create_result = await self.user_create_by_qq(qq)

        if create_result is not None:
            return create_result["uuid"]

        return None

    async def get_current_maimai_bind_info(self, uuid: str) -> MaimaiBindInfo | None:
        """
        获取用户当前选择的maimai绑定的所有相关绑定

        Args:
            uuid: 用户的uuid

        Returns:
            成功返回响应JSON，失败返回None
        """

        resp = await self._client.get(
            "/v1/maimai/get-current-maimai-bind", params={"uuid": uuid}
        )

        if resp.status_code == 200:
            result: list[V1MaimaiGetCurrentMaimaiBindResponseSingle] = resp.json()
            return self._v1_maimai_get_current_maimai_bind_response_2_maimai_bind_info(
                result
            )

        return None

    async def update_current_maimai_bind(
        self,
        uuid: str,
        divingfish_bind_name: str | None = None,
        luoxue_bind_name: str | None = None,
    ) -> MaimaiBindInfo | None:
        resp = await self._client.get(
            "/v1/maimai/update-current-maimai-bind",
            params={
                "uuid": uuid,
                "divingfish_bind_name": divingfish_bind_name,
                "luoxue_bind_name": luoxue_bind_name,
            },
        )

        if resp.status_code == 200:
            result: list[V1MaimaiGetCurrentMaimaiBindResponseSingle] = resp.json()
            return self._v1_maimai_get_current_maimai_bind_response_2_maimai_bind_info(
                result
            )

        return None

    async def switch_current_maimai_bind(
        self, uuid: str, mai_bind_name: str
    ) -> MaimaiBindInfo | None:
        """
        切换用户当前maimai档案
        """
        resp = await self._client.get(
            "/v1/maimai/switch-current-maimai-bind",
            params={"uuid": uuid, "bind_name": mai_bind_name},
        )

        if resp.status_code == 200:
            result: list[V1MaimaiGetCurrentMaimaiBindResponseSingle] = resp.json()
            return self._v1_maimai_get_current_maimai_bind_response_2_maimai_bind_info(
                result
            )

        return None

    @staticmethod
    def _v1_maimai_get_current_maimai_bind_response_2_maimai_bind_info(
        resp: list[V1MaimaiGetCurrentMaimaiBindResponseSingle],
    ):
        maimai_bind = None
        for bind in resp:
            if bind["bind_type"] == UserBindType.MaimaiCN:
                maimai_bind = bind
                break
        if not maimai_bind:
            return None
        resp.remove(maimai_bind)

        return MaimaiBindInfo(maimai=maimai_bind, others=resp)

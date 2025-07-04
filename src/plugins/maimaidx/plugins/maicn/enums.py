from enum import StrEnum


class EndPointV1(StrEnum):
    """
    API endpoint枚举
    """
    ADD_USER_BIND = "/v1/user/add-bind"
    USER_GET_UUID = "/v1/user/get-uuid"
    MAIMAICN_GET_UID = "/v1/maimaicn/get-uid"
    USER_CREATE_BY_QQ = "/v1/user/create-by-qq"


class UserBindType(StrEnum):
    """
    用户绑定类型枚举
    """
    QQ = "qq"
    DivingFish = "divingfish"
    Luoxue = "luoxue"
    MaimaiCN = "maimai_cn"
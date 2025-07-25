from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    remi_service_base_url: str

    diving_fish_developer_token: str
    lxns_developer_token: str

    lxns_base_url: str

    maimai_arcade_chip_id: str
    maimai_arcade_aes_key: str
    maimai_arcade_aes_iv: str
    maimai_arcade_obfuscate_param: str

    proxy_host: str
    proxy_port: int
    proxy_username: str
    proxy_password: str

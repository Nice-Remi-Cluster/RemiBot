from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    remi_service_base_url: str

    diving_fish_developer_token: str
    lxns_developer_token: str

    maimai_arcade_chip_id: str
    maimai_arcade_aes_key: str
    maimai_arcade_aes_iv: str
    maimai_arcade_obfuscate_param: str


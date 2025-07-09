from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    lxns_developer_token: str
    lxns_base_url: str
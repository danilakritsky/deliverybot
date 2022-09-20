from pydantic import BaseSettings
from pydantic import SecretStr as SecretStr


class Config(BaseSettings):
    BOT_TOKEN: SecretStr

    class Config:
        env_file: str
        env_file_encoding: str

CONFIG: Config

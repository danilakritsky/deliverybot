from pydantic import BaseSettings, SecretStr


class Config(BaseSettings):
    BOT_TOKEN: SecretStr

    # https://progressstory.com/tech/python/configuration-management-python-pydantic/
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


CONFIG: Config = Config()

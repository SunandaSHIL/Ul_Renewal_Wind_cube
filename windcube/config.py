from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = "./.env"


class Settings(BaseSettings):
    CLIENT_ORIGIN: str

    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()


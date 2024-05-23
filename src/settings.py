from pydantic import BaseSettings, Field, HttpUrl


class Settings(BaseSettings):
    API_HOST: HttpUrl = Field(
        default="https://www.googleapis.com/youtube/v3/channels?part=statistics",
        description="URL of the reference to connect through YouTube.",
    )
    CHANNEL_ID = Field(
        default="",
        description="Youtube Channel to check the subscribers.",
    )
    API_KEY = Field(
        default="",
        description="Youtube Date API Key to use on requests.",
    )

    class Config:
        env_prefix = "SUBS_"
        case_sensitive = False
        env_file = ".env"


settings = Settings()

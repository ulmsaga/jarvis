from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Slack (필수)
    slack_bot_token: str
    slack_signing_secret: str

    # GitHub (PR 자동 생성용)
    github_token: str = ""
    github_owner: str = "ulmsaga"
    github_repo: str = "vizops"

    # Server
    host: str = "0.0.0.0"
    port: int = 3000


settings = Settings()

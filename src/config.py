from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Slack
    slack_bot_token: str
    slack_signing_secret: str
    slack_app_token: str = ""

    # OpenAI (Brain / Codex)
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Anthropic (Claude Code / Skills)
    anthropic_api_key: str
    claude_model: str = "claude-opus-4-7"

    # GitHub
    github_token: str = ""
    github_owner: str = ""
    github_repo: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 3000


settings = Settings()

"""Slack Bolt async 앱 초기화"""
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from src.config import settings
from src.slack import events

app = AsyncApp(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
)

events.register(app)

handler = AsyncSlackRequestHandler(app)

import os
from discord_webhook import DiscordWebhook

def notify_discord(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        webhook.execute()

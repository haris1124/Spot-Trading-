# telegram_client.py

import aiohttp

class Telegram:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def send_message(self, message):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                return resp.status == 200
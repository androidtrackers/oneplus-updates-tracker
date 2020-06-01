from time import sleep
from typing import List

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater

from op_tracker.official.models.update import Update


class TelegramBot:
    def __init__(self, bot_token, chat):
        self.bot = Bot(token=bot_token)
        self.updater = Updater(bot=self.bot, use_context=True)
        self.chat = chat

    def post_updates(self, new_updates: List[Update]):
        for update in new_updates:
            message, button = self.generate_update_message(update)
            self.send_telegram_message(message, button)

    @staticmethod
    def generate_update_message(update: Update):
        message: str = f"New update available!\n" \
                       f"*Device*: {update.device}\n" \
                       f"*Region*: {update.region}\n" \
                       f"*Branch*: {update.type}\n" \
                       f"*Version*: {update.version}\n" \
                       f"*Release Date*: {update.updated}\n" \
                       f"*Size*: {update.size}\n" \
                       f"*MD5*: `{update.md5}`\n" \
                       f"*Changlog*:\n{update.changelog}"
        button: InlineKeyboardButton = InlineKeyboardButton(f"Download", update.link)
        return message, InlineKeyboardMarkup([[button]])

    def send_telegram_message(self, message, reply_markup):
        self.updater.bot.send_message(chat_id=self.chat, text=message,
                                      parse_mode='Markdown', disable_web_page_preview='yes',
                                      reply_markup=reply_markup)
        sleep(5)

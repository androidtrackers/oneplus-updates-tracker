"""Telegram Bot implementation"""
from time import sleep
from typing import List, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater

from op_tracker.common.database.database import get_incremental
from op_tracker.common.database.models.update import Update


class TelegramBot:
    """
    This class implements telegram bot that is used for sending updates to a telegram chat
    :attr:`bot` Telegram bot object
    :attr:`updater` Telegram updater object
    :attr:`chat` Telegram chat username or id
    """

    def __init__(self, bot_token: str, chat: Union[int, str], source: str):
        """
        TelegramBot class constructor
        :param bot_token: Telegram Bot API access token
        :param chat: Telegram chat username or id that will be used to send updates to
        """
        self.updater = Updater(token=bot_token, use_context=True)
        self.chat = chat if isinstance(chat, int) else f"@{chat}"
        self.source = source

    def post_updates(self, new_updates: List[Update]):
        """
        Send updates to a Telegram chat
        :param new_updates: a list of updates
        :return: None
        """
        for update in new_updates:
            message, button = self.generate_message(update)
            self.send_telegram_message(message, button)

    def generate_message(self, update: Update) -> (str, InlineKeyboardMarkup):
        """
        Generate an update message from and `Update` object
        :param update: an Update object that contains update's information from official website
        :return: A string containing the update's message
         and inline keyboard that has download link'
        """
        message: str = f"New update available!"
        if self.source == "website":
            message += " (on the official website)\n"
        elif self.source == "updater":
            message += " (via OTA)\n"
        else:
            message += "\n"
        message += (
            f"*Device*: {update.device}\n"
            f"*Region*: {update.region}\n"
            f"*Type*: {update.branch}\n"
            f"*Version*: ```{update.version}```\n"
            f"*Release Date*: {update.date}\n"
            f"*Size*: {update.size}\n"
            f"*MD5*: `{update.md5}`\n"
            f"*Changelog*:\n```{update.changelog}```"
        )
        button: InlineKeyboardButton = InlineKeyboardButton("Full ROM", update.link)
        incremental = get_incremental(update.version)
        if incremental:
            incremental_button: InlineKeyboardButton = InlineKeyboardButton(
                "Incremental", incremental.link
            )
            return message, InlineKeyboardMarkup([[button], [incremental_button]])
        return message, InlineKeyboardMarkup([[button]])

    def send_telegram_message(self, message: str, reply_markup: InlineKeyboardMarkup):
        """
        Send a message to Telegram chat
        :param message: A string of the update message to be sent
        :param reply_markup: A inline keyboard markup object that contains the update list
        :return:
        """
        self.updater.bot.send_message(
            chat_id=self.chat,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview="yes",
            reply_markup=reply_markup,
        )
        sleep(5)

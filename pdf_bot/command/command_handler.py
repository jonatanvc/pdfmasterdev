from telegram.ext import BaseHandler, CommandHandler, filters

from pdf_bot.stats import StatsService
from pdf_bot.telegram_handler import AbstractTelegramHandler

from .command_service import CommandService


class MyCommandHandler(AbstractTelegramHandler):
    _START_COMMAND = "start"
    _HELP_COMMAND = "help"
    _SEND_COMMAND = "send"
    _STATS_COMMAND = "stats"
    _VPS_COMMAND = "vps"

    def __init__(
        self,
        command_service: CommandService,
        stats_service: StatsService,
        admin_telegram_id: int,
    ) -> None:
        self.command_service = command_service
        self.stats_service = stats_service
        self.admin_telegram_id = admin_telegram_id

    @property
    def handlers(self) -> list[BaseHandler]:
        return [
            CommandHandler(self._START_COMMAND, self.command_service.send_start_message),
            CommandHandler(self._HELP_COMMAND, self.command_service.send_help_message),
            CommandHandler(
                self._SEND_COMMAND,
                self.command_service.send_message_to_user,
                filters.User(self.admin_telegram_id),
            ),
            CommandHandler(
                self._STATS_COMMAND,
                self.stats_service.send_bot_stats,
                filters.User(self.admin_telegram_id),
            ),
            CommandHandler(
                self._VPS_COMMAND,
                self.stats_service.send_vps_stats,
                filters.User(self.admin_telegram_id),
            ),
        ]

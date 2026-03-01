from typing import Any

import sentry_sdk
from dependency_injector.providers import Singleton
from dependency_injector.wiring import Provide, inject
from loguru import logger
from telegram.ext import Application as TelegramApp

from pdf_bot.containers import Application
from pdf_bot.database import DatabaseClient
from pdf_bot.error import ErrorHandler
from pdf_bot.log import MyLogHandler
from pdf_bot.settings import Settings
from pdf_bot.telegram_handler import AbstractTelegramHandler


@inject
def main(
    telegram_app: TelegramApp,
    settings: Settings | dict[str, Any] = Provide[Application.core.settings],
    log_handler: MyLogHandler = Provide[Application.core.log_handler],
    db_client: DatabaseClient = Provide[Application.clients.database],
) -> None:
    log_handler.setup()

    # There's a bug where configurations are passed as a dict, so we attempt to pass it
    # here. See https://github.com/ets-labs/python-dependency-injector/issues/593
    if isinstance(settings, dict):
        settings = Settings(**settings)

    # Initialize PostgreSQL database tables
    if db_client.check_connection():
        db_client.create_tables()
        logger.info("PostgreSQL database initialized successfully")
    else:
        logger.error("Failed to connect to PostgreSQL database")

    if settings.sentry_dsn is not None:
        sentry_sdk.init(settings.sentry_dsn, traces_sample_rate=0.8, profiles_sample_rate=0.8)
    else:
        logger.warning("SENTRY_DSN not set")

    telegram_app.run_polling()


if __name__ == "__main__":
    import os
    import sys

    # Verify required environment variables before starting
    required_vars = ["TELEGRAM_TOKEN", "DATABASE_URL", "ADMIN_TELEGRAM_ID"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        logger.error("Missing required environment variables: {vars}", vars=", ".join(missing))
        logger.error("Set them in Dokploy Environment tab or in .env file")
        sys.exit(1)

    logger.info("Starting PDF Bot...")

    try:
        app = Application()
    except Exception:
        logger.exception("Failed to create Application container")
        sys.exit(1)

    app.wire(modules=[__name__])

    _telegram_app = (
        TelegramApp.builder().bot(app.core.telegram_bot()).concurrent_updates(True).build()
    )

    # Dependency injectior only initialises the classes if they are referenced. Since
    # the processors are not referenced anywhere, we need to explicitly initialise them
    # so that they're registered under AbstractFileProcessor
    for provider in app.processors.providers.values():  # type: ignore[attr-defined]
        if isinstance(provider, Singleton):
            provider()

    # Similarly, initialise and register all the handlers for the bot
    for provider in app.handlers.providers.values():  # type: ignore[attr-defined]
        if isinstance(provider, Singleton):
            handler = provider()
            if isinstance(handler, AbstractTelegramHandler):
                _telegram_app.add_handlers(handler.handlers)
            elif isinstance(handler, ErrorHandler):
                _telegram_app.add_error_handler(handler.callback)

    main(_telegram_app)

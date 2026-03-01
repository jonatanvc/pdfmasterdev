from typing import Any

from requests import Session

from pdf_bot.settings import Settings


class AnalyticsRepository:
    def __init__(self, api_client: Session, settings: Settings | dict[str, Any]) -> None:
        self.api_client = api_client

        # There's a bug where configurations are passed as a dict, so we attempt to pass
        # it here. See https://github.com/ets-labs/python-dependency-injector/issues/593
        if isinstance(settings, dict):
            settings = Settings(**settings)

        self._enabled = bool(settings.ga_api_secret and settings.ga_measurement_id)
        self.request_params = {
            "api_secret": settings.ga_api_secret or "",
            "measurement_id": settings.ga_measurement_id or "",
        }

    def send_event(self, event: dict[str, Any]) -> None:
        if not self._enabled:
            return
        self.api_client.post(
            "https://www.google-analytics.com/mp/collect",
            params=self.request_params,
            json=event,
            timeout=10,
        )

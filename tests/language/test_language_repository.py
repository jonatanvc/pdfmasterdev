from typing import Any, ClassVar
from unittest.mock import MagicMock

from pdf_bot.consts import LANGUAGE
from pdf_bot.database import DatabaseClient
from pdf_bot.database.models import UserModel
from pdf_bot.language import LanguageRepository


class TestLanguageRepository:
    USER_ID = 0
    LANGUAGE_CODE = "lang_code"

    def setup_method(self) -> None:
        self.db_client = MagicMock(spec=DatabaseClient)
        self.mock_session = MagicMock()
        self.db_client.get_session.return_value.__enter__ = MagicMock(
            return_value=self.mock_session
        )
        self.db_client.get_session.return_value.__exit__ = MagicMock(return_value=False)
        self.sut = LanguageRepository(self.db_client)

    def test_get_language(self) -> None:
        mock_user = MagicMock(spec=UserModel)
        mock_user.language = self.LANGUAGE_CODE
        self.mock_session.get.return_value = mock_user

        actual = self.sut.get_language(self.USER_ID)

        assert actual == self.LANGUAGE_CODE

    def test_get_language_without_user(self) -> None:
        self.mock_session.get.return_value = None
        actual = self.sut.get_language(self.USER_ID)
        assert actual == self.sut.EN_GB_CODE

    def test_get_language_and_language_not_set(self) -> None:
        mock_user = MagicMock(spec=UserModel)
        mock_user.language = None
        self.mock_session.get.return_value = mock_user

        actual = self.sut.get_language(self.USER_ID)
        assert actual == self.sut.EN_GB_CODE

    def test_get_language_legacy_en_code(self) -> None:
        mock_user = MagicMock(spec=UserModel)
        mock_user.language = "en"
        self.mock_session.get.return_value = mock_user

        actual = self.sut.get_language(self.USER_ID)

        assert actual == self.sut.EN_GB_CODE

    def test_upsert_language(self) -> None:
        self.sut.upsert_language(self.USER_ID, self.LANGUAGE_CODE)
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()

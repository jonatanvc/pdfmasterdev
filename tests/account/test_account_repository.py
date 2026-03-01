from unittest.mock import MagicMock, patch

from pdf_bot.account import AccountRepository
from pdf_bot.consts import LANGUAGE
from pdf_bot.database import DatabaseClient
from pdf_bot.database.models import UserModel


class TestAccountRepository:
    USER_ID = 0
    LANGUAGE_CODE = "lang_code"

    def setup_method(self) -> None:
        self.db_client = MagicMock(spec=DatabaseClient)
        self.mock_session = MagicMock()
        self.db_client.get_session.return_value.__enter__ = MagicMock(
            return_value=self.mock_session
        )
        self.db_client.get_session.return_value.__exit__ = MagicMock(return_value=False)
        self.sut = AccountRepository(self.db_client)

    def test_get_user(self) -> None:
        mock_user = MagicMock(spec=UserModel)
        mock_user.language = self.LANGUAGE_CODE
        self.mock_session.get.return_value = mock_user

        actual = self.sut.get_user(self.USER_ID)

        assert actual is not None
        assert actual[LANGUAGE] == self.LANGUAGE_CODE

    def test_get_user_null(self) -> None:
        self.mock_session.get.return_value = None
        actual = self.sut.get_user(self.USER_ID)
        assert actual is None

    def test_upsert_user(self) -> None:
        self.sut.upsert_user(self.USER_ID, self.LANGUAGE_CODE)
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()

from unittest.mock import MagicMock, patch

from pdf_bot.database import DatabaseClient


class TestDatabaseClient:
    def test_init(self) -> None:
        database_url = "postgresql://user:pass@localhost:5432/testdb"

        with patch("pdf_bot.database.connection.create_engine") as mock_engine:
            client = DatabaseClient(database_url)

            mock_engine.assert_called_once()
            assert client._database_url == database_url

    def test_check_connection(self) -> None:
        database_url = "postgresql://user:pass@localhost:5432/testdb"

        with patch("pdf_bot.database.connection.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_engine.return_value.connect.return_value.__enter__ = MagicMock(
                return_value=mock_conn
            )
            mock_engine.return_value.connect.return_value.__exit__ = MagicMock(return_value=False)

            client = DatabaseClient(database_url)
            result = client.check_connection()

            assert result is True

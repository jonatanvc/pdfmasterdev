from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from pdf_bot.consts import LANGUAGE
from pdf_bot.database import DatabaseClient
from pdf_bot.database.models import UserModel


class AccountRepository:
    def __init__(self, db_client: DatabaseClient) -> None:
        self.db_client = db_client

    def get_user(self, user_id: int) -> dict | None:
        with self.db_client.get_session() as session:
            user = session.get(UserModel, user_id)
            if user is None:
                return None
            return {LANGUAGE: user.language}

    def upsert_user(self, user_id: int, language_code: str) -> None:
        with self.db_client.get_session() as session:
            try:
                stmt = insert(UserModel).values(
                    user_id=user_id,
                    language=language_code,
                )
                # Only set language if the user doesn't exist yet (don't overwrite)
                stmt = stmt.on_conflict_do_nothing(index_elements=["user_id"])
                session.execute(stmt)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception("Failed to upsert user {user_id}", user_id=user_id)
                raise

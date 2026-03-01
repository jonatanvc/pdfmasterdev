from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from pdf_bot.database import DatabaseClient
from pdf_bot.database.models import UserModel


class LanguageRepository:
    EN_GB_CODE = "en_GB"
    EN_CODE = "en"

    def __init__(self, db_client: DatabaseClient) -> None:
        self.db_client = db_client

    def get_language(self, user_id: int) -> str:
        with self.db_client.get_session() as session:
            user = session.get(UserModel, user_id)

            if user is None or user.language is None:
                return self.EN_GB_CODE

            lang: str = user.language

            # This check is for backwards compatibility
            if lang == self.EN_CODE:
                return self.EN_GB_CODE
            return lang

    def upsert_language(self, user_id: int, language_code: str) -> None:
        with self.db_client.get_session() as session:
            try:
                stmt = insert(UserModel).values(
                    user_id=user_id,
                    language=language_code,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["user_id"],
                    set_={"language": language_code},
                )
                session.execute(stmt)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception(
                    "Failed to upsert language for user {user_id}", user_id=user_id
                )
                raise

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from pdf_bot.database.models import Base


class DatabaseClient:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    def create_tables(self) -> None:
        """Create all database tables if they don't exist."""
        Base.metadata.create_all(self._engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self._session_factory()

    def check_connection(self) -> bool:
        """Check if the database connection is working."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception:
            logger.exception("Database connection failed")
            return False
        else:
            return True

import logging
import os
import time
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

if os.getenv("TESTING") == "true":
    SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    from app.constants import DATABASE_URL
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        connect_args={"connect_timeout": 10}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    quadrant = Column(Integer, nullable=False)
    done = Column(Boolean, default=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database(retries: int = 10, delay_seconds: int = 3):
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database is initialized")
            return
        except OperationalError as error:
            if attempt == retries:
                logger.exception("Database is not available after %s attempts", retries)
                raise
            logger.warning(
                "Database is not ready, retrying in %ss (%s/%s): %s",
                delay_seconds,
                attempt,
                retries,
                error,
            )
            time.sleep(delay_seconds)

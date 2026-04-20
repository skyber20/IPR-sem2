import pytest
from sqlalchemy import inspect
from app.database import TaskDB, Base, engine
from sqlalchemy.orm import sessionmaker


def test_taskdb_model():
    """Проверяем создание модели TaskDB"""
    task = TaskDB(
        id=1,
        text="Тестовая задача",
        quadrant=1,
        done=False
    )
    assert task.id == 1
    assert task.text == "Тестовая задача"
    assert task.quadrant == 1
    assert task.done is False


def test_database_tables():
    """Проверяем создание таблиц"""
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "tasks" in tables

    Base.metadata.drop_all(bind=engine)


def test_get_db():
    """Проверяем функцию get_db"""
    from app.database import get_db

    db_gen = get_db()
    db = next(db_gen)

    assert db is not None
    assert hasattr(db, "query")

    try:
        next(db_gen)
    except StopIteration:
        pass
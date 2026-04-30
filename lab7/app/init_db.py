import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.database import engine, Base

def init_db():
    """Создает все таблицы в базе данных"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно!")

if __name__ == "__main__":
    init_db()
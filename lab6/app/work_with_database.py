from app.database import get_db, TaskDB
from app.models.task import Task


class DatabaseManager:
    def __init__(self):
        pass

    def read_json(self) -> list[Task]:
        """Читаем задачи из БД (оставляем старое название для совместимости)"""
        db = next(get_db())
        try:
            tasks_db = db.query(TaskDB).all()
            tasks = []
            for task_db in tasks_db:
                task = Task(
                    id=task_db.id,
                    text=task_db.text,
                    quadrant=task_db.quadrant,
                    done=task_db.done
                )
                tasks.append(task)
            return tasks
        finally:
            db.close()

    def load_json(self, tasks: list[Task]) -> None:
        """Сохраняем задачи в БД (оставляем старое название для совместимости)"""
        db = next(get_db())
        try:
            db.query(TaskDB).delete()

            for task in tasks:
                task_db = TaskDB(
                    id=task.id,
                    text=task.text,
                    quadrant=task.quadrant,
                    done=task.done
                )
                db.add(task_db)

            db.commit()
        finally:
            db.close()

    def add_task(self, task: Task) -> None:
        """Добавить одну задачу"""
        db = next(get_db())
        try:
            task_db = TaskDB(
                id=task.id,
                text=task.text,
                quadrant=task.quadrant,
                done=task.done
            )
            db.add(task_db)
            db.commit()
        finally:
            db.close()

    def update_task_done(self, task_id: int, done: bool) -> None:
        """Обновить статус задачи"""
        db = next(get_db())
        try:
            task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if task_db:
                task_db.done = done
                db.commit()
        finally:
            db.close()

    def delete_task(self, task_id: int) -> None:
        """Удалить задачу"""
        db = next(get_db())
        try:
            task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if task_db:
                db.delete(task_db)
                db.commit()
        finally:
            db.close()

    def update_task_quadrant(self, task_id: int, quadrant: int) -> None:
        """Обновить квадрант задачи"""
        db = next(get_db())
        try:
            task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if task_db:
                task_db.quadrant = quadrant
                db.commit()
        finally:
            db.close()
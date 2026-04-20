import logging
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db, TaskDB, init_database
from app.models.task import Task, CreateTask, NewQuadrant
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_database()
app = FastAPI()

@app.middleware("http")
async def disable_static_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith(('.js', '.css', '.html')):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")


@app.get('/get_tasks')
def get_all_tasks(db: Session = Depends(get_db)):
    logger.info('я в получении тасок')
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


@app.post('/add_task')
async def add_new_task(data_to_create_task: CreateTask, db: Session = Depends(get_db)):
    logger.info('я в добавлении таски')

    new_id = int(datetime.now().timestamp())
    new_task_db = TaskDB(
        id=new_id,
        text=data_to_create_task.text,
        quadrant=data_to_create_task.quadrant,
        done=False
    )

    db.add(new_task_db)
    db.commit()

    new_task = Task(
        id=new_task_db.id,
        text=new_task_db.text,
        quadrant=new_task_db.quadrant,
        done=new_task_db.done
    )

    return new_task


@app.put('/done_task/{task_id}')
async def update_done_task(task_id: int, db: Session = Depends(get_db)):
    logger.info('я меняю состояние done')

    task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task_db:
        task_db.done = not task_db.done
        db.commit()
        logger.info('я поменял состояние done')


@app.delete('/delete_task/{task_id}')
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    logger.info('я буду удалять таску')

    task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task_db:
        db.delete(task_db)
        db.commit()
        logger.info('удалил таску')


@app.put('/move_task/{task_id}')
async def move_task(task_id: int, new_quadrant: NewQuadrant, db: Session = Depends(get_db)):
    logger.info('я буду перемещать задачу в другой квадрант')

    task_db = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task_db:
        task_db.quadrant = new_quadrant.quadrant
        db.commit()
        logger.info('я переместил таску в новый квадрант')


@app.get('/health')
def get_health():
    logger.info('я проверяю здоровье')
    return {
        'status': 'healthy'
    }


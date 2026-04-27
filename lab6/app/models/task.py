from pydantic import BaseModel


class CreateTask(BaseModel):
    text: str
    quadrant: int


class Task(BaseModel):
    id: int
    text: str
    quadrant: int
    done: bool


class NewQuadrant(BaseModel):
    quadrant: int

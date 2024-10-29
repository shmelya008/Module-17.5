from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import User
from app.models.task import Task
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Task was not found')
    else:
        return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, cre_task: CreateTask):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    db.execute(insert(Task).values(title=cre_task.title,
                                   content=cre_task.content,
                                   priority=cre_task.priority,
                                   user_id=user_id,
                                   slug=slugify(cre_task.title)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, upd_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Task was not found')
    db.execute(update(Task).where(Task.id == task_id).values(title=upd_task.title,
                                                             content=upd_task.content,
                                                             priority=upd_task.priority))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task updated successfully'
    }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Task was not found')
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task deleted successfully'
    }


# @router.delete('/delete_all')
# async def delete_all_tasks(db: Annotated[Session, Depends(get_db)]):
#     db.execute(delete(Task))
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'All tasks have been successfully deleted.'
#     }

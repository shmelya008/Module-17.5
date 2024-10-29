from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import Task
from app.models.user import User
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    else:
        return user


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    else:
        tasks = db.scalar(select(Task).where(Task.id == user_id))
        return tasks


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], username: str, cre_user: CreateUser):
    username = db.scalar(select(User).where(User.username == username))
    if username is not None:
        raise HTTPException(status_code=status.HTTP_306_RESERVED,
                            detail='This user already exists')
    db.execute(insert(User).values(username=cre_user.username,
                                   firstname=cre_user.firstname,
                                   lastname=cre_user.lastname,
                                   age=cre_user.age,
                                   slug=slugify(cre_user.username)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, upd_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    db.execute(update(User).where(User.id == user_id).values(firstname=upd_user.firstname,
                                                             lastname=upd_user.lastname,
                                                             age=upd_user.age))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User updated is successfully'
    }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User deleted successfully'
    }


# @router.delete('/delete_all')
# async def delete_all_users(db: Annotated[Session, Depends(get_db)]):
#     db.execute(delete(User))
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'All users have been successfully deleted.'
#     }

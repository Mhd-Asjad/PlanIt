from fastapi import HTTPException , Depends , status , APIRouter
from database.schemas.task import Task , UpdateTask
from database.db_config import db , task
from database.schemas.user import LoginRequest
from typing import Annotated 
from datetime import datetime
from .deps import current_user
from auth.utils.counter import get_next_sequence
from loguru import logger

router = APIRouter()

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_task(task: Task , current_user: Annotated[LoginRequest , Depends(current_user)]):
    try:
        
        logger.info(f"task data : {task}")
        task_data = task.dict()
        task_data['user_id'] = str(current_user.get('id'))
        tast_id = get_next_sequence("task_id")
        task_data['id'] = tast_id
        
        db.task.insert_one(task_data)
        logger.info(f"Task created : {task_data}")
        return {"status": status.HTTP_201_CREATED, "detail": "Task created successfully", "task_id": tast_id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
            
        )
        
@router.get('/list', status_code=status.HTTP_200_OK)
async def list_tasks(current_user: Annotated[LoginRequest , Depends(current_user)]):
    logger.info(f'user has been updated with the current user:{current_user}')

    try:
        user_id = str(current_user.get('id'))
        logger.info(f"Retrieving tasks for user ID: {user_id}") 
        tasks = list(db.task.find({"user_id": str(user_id)}, {"_id": 0}))
        logger.info(f"Tasks retrieved for user {user_id}: {tasks}")
        return {"status": status.HTTP_200_OK, "tasks": tasks}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tasks: {str(e)}"
        )
        
@router.patch('/update/{task_id}', status_code=status.HTTP_200_OK)
async def update_task(
    current_user: Annotated[LoginRequest , Depends(current_user)],
    task_id: int,
    task_data: UpdateTask,
  ):
    try:
        logger.info(f"this task_id : {task_id} task_data : {task_data}")
        user_id = str(current_user.get('id'))
        logger.info(f"user id getting as type : {type(user_id)}")
        filter_query = {'id': task_id, 'user_id': user_id}
        logger.info(f"filter query : {filter_query}")
        existing_task = db.task.find(filter_query, {"_id": 0})
        logger.info(f"existing task : {existing_task}")
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"task not found for updating"
            )

        updated_data = task_data.dict(exclude_unset=True)
        if not updated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update provided."
            )
        logger.info(f"new task to update : {updated_data}")
        updated_data['updated_at'] = datetime.utcnow().replace(tzinfo=None)
        logger.info(f"updated data with timestamp : {updated_data}")
        res = db.task.update_one(
            {'id': int(task_id) , 'user_id': str(user_id)} ,
            {"$set": updated_data},
        )
        logger.info(f"Update result: matched={res.matched_count}, modified={res.modified_count}")

        if res.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task update failed or no changes were made.",
            )
        return {"status" : 200 , "detail": "task updated sucessfully"}
    
    except Exception as error:
        logger.info(f"updating error : {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error while updating task : {str(error)} "
        )
        
@router.delete('/delete/{task_id}', status_code=status.HTTP_200_OK)
async def delete(
    task_id: str,
    current_user: Annotated[LoginRequest, Depends(current_user)]   
  ):
    
    try:
        user_id = current_user.get('id')
        logger.info(f'type of the user_id :{type(user_id)} task_id : {type(task_id)}')
        filter_query = {'id': int(task_id), 'user_id': str(user_id)}
        deleted_task = db.task.delete_one(filter_query)

        logger.info(f'deleted_task: {deleted_task}')
        if deleted_task.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or already deleted"
            )
        return {'status_code': 200 , 'detail':"task deleted successfully"}

    except Exception as e:
        return HTTPException(
            status_code=200,
            detail=f"error occur while deleting task : {str(e)}"
        )
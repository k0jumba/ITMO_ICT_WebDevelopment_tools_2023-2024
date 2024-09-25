from fastapi import APIRouter, status, HTTPException
from celery_app import parse_user
from dotenv import load_dotenv
import os
from models import UserSerialized


router = APIRouter()

load_dotenv()
parser_url = os.getenv("PARSER_URL")


@router.post("/parser", status_code=status.HTTP_201_CREATED)
def call_parser() -> dict:
    task = parse_user.delay()
    return {"task_id": task.id}


@router.get("/parser_results/{task_id}")
def get_result(task_id: str) -> UserSerialized:
    task = parse_user.AsyncResult(task_id)
    if task.status == "PENDING":
        raise HTTPException(status_code=202, detail="Task is still being processed.")
    elif task.status == "FAILURE":
        raise HTTPException(status_code=500, detail="Task failed.")
    else:
        user_data = task.result
        return UserSerialized(id=user_data.get("id"),
                              email=user_data.get("email"),
                              first_name=user_data.get("first_name"),
                              last_name=user_data.get("last_name"))

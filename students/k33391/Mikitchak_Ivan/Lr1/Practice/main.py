from fastapi import FastAPI
from typing import List
from typing_extensions import TypedDict
from models import (
    Warrior,
)

app = FastAPI()


temp_bd = [
{
    "id": 1,
    "race": "director",
    "name": "Martynov Dmitrij",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "A powerful figure",
        "description": "An all-matters expert"
    },
    "skills":
        [{
            "id": 1,
            "name": "Selling compressors",
            "description": ""

        },
        {
            "id": 2,
            "name": "Evaluating property",
            "description": ""

        }]
},
{
    "id": 2,
    "race": "worker",
    "name": "Andrey Kosyakin",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Delphi workhorse",
        "description": "A respected employee"
    },
    "skills": []
},
]


@app.get("/")
def hello():
    return "Hello, [username]!"

@app.get("/warriors")
def warrior_list() -> List[Warrior]:
    return temp_bd

@app.get("/warriors/{warrior_id}")
def warrior_retrieve(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]

@app.post("/warriors")
def warrior_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}

@app.delete("/warriors/{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}

@app.put("/warriors/{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd

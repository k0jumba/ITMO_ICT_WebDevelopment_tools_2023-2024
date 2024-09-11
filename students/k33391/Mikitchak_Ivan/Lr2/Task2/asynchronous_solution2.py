import asyncio
import aiohttp
import asyncpg
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import time

# URL for fetching generated user data
URL = "https://randomuser.me/api/?format=json"

# Utility for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def fetch_data(session):
    try:
        async with session.get(URL) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data
                except Exception as e:
                    print(f"An error occurred while decoding JSON: {e}")
                    return None
            else:
                print(f"Request failed with status code {response.status}")
                return None
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def extract_user(data):
    try:
        user = {
            "email": data["results"][0]["email"],
            "hashed_password": hash_password(data["results"][0]["login"]["password"]),
            "first_name": data["results"][0]["name"]["first"],
            "last_name": data["results"][0]["name"]["last"]
        }
        return user
    except Exception as e:
        print(f"An error occurred while extracting user: {e}")
        return None

async def store_user(user):
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME2"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        await conn.execute(
            "INSERT INTO app_user (email, hashed_password, first_name, last_name) VALUES ($1, $2, $3, $4)",
            user["email"], user["hashed_password"], user["first_name"], user["last_name"]
        )
        await conn.close()
    except Exception as e:
        print(f"An error occurred while storing user: {e}")

async def parse_and_save(session):
    data = await fetch_data(session)
    if data is None:
        return
    user = extract_user(data)
    if user is None:
        return
    await store_user(user)
    print(user)

async def main():
    load_dotenv()

    n_tasks = 4
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(n_tasks):
            task = parse_and_save(session)
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    finish = time.time()
    print(f"Time: {finish - start}")
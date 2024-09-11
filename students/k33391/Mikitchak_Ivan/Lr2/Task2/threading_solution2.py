import threading
import requests
import psycopg2
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import time

# URL for fetching generated user data
URL = "https://randomuser.me/api/?format=json"

# Utility for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

log_lock = threading.Lock()

def log(msg):
    with log_lock:
        print(msg)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def fetch_data(session):
    try:
        response = session.get(URL)
        if response.status_code == 200:
            try:
                data = response.json()
                return data
            except Exception as e:
                print(f"An error occurred while decoding JSON: {e}")
                return None
        else:
            print(f"Request failed with status code {response.status_code}")
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

def store_user(user):
    try:
        with psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME2"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO app_user (email, hashed_password, first_name, last_name) VALUES (%s, %s, %s, %s)",
                    (user["email"], user["hashed_password"], user["first_name"], user["last_name"])
                )
                conn.commit()
    except Exception as e:
        print(f"An error occurred while storing user: {e}")

def parse_and_save(session):
    data = fetch_data(session)
    if data is None:
        return
    user = extract_user(data)
    if user is None:
        return
    store_user(user)
    log(user)

def main():
    load_dotenv()
    
    n_tasks = 4
    with requests.Session() as session:
        threads = []
        for _ in range(n_tasks):
            thread = threading.Thread(target=parse_and_save, args=(session,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == "__main__":
    start = time.time()
    main()
    finish = time.time()
    print(f"Time: {finish - start}")

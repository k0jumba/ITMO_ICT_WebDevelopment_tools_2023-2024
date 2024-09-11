import time
import threading
import requests
import psycopg2
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


log_lock = threading.Lock()

def log(msg):
    with log_lock:
        print(msg)

def fetch_html(session, url):
    try:
        response = session.get(url)
        if response.status_code == 200:
            try:
                text = response.text
                return text
            except Exception as e:
                print(f"An error occurred while decoding text for {url}: {e}")
                return None
        else:
            print(f"Request to {url} failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching html from {url}: {e}")
        return None

def extract_headers(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        head = soup.head
        return str(head) if head else None
    except Exception as e:
        print(f"An error occurred while extracting headers: {e}")
        return None

def store_headers(url, headers):
    try:
        with psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME1"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),            
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO html_headers (url, header_content) VALUES (%s, %s)", (url, headers))
            conn.commit()
    except Exception as e:
        print(f"Failed to store headers for {url}: {e}")

def parse_and_save(session, url):
    html = fetch_html(session, url)
    if html is None:
        return
    headers = extract_headers(html)
    if headers is None:
        return
    store_headers(url, headers)
    log(f"Headers for {url}:\n{headers}\n\n\n\n\n")

def main():
    urls = ["https://example.com", "https://www.gnu.org", "https://www.wikipedia.org", "https://toscrape.com"]
    load_dotenv()
    
    with requests.Session() as session:
        threads = []
        for url in urls:
            thread = threading.Thread(target=parse_and_save, args=(session, url))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    
if __name__ == "__main__":
    start = time.time()
    main()
    finish = time.time()    
    print(f"Time: {finish - start}")

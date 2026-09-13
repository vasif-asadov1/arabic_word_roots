import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")

thread_local = threading.local()
global_lock = threading.Lock()
is_cooling_down = False

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        thread_local.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Referer": "https://www.almaany.com/",
            "Connection": "keep-alive"
        })
    return thread_local.session

def setup_database(cursor):
    try:
        cursor.execute("ALTER TABLE roots ADD COLUMN almaany_en TEXT")
        print("✅ Verified 'almaany_en' column.")
    except sqlite3.OperationalError:
        pass

def fetch_almaany(spaced_root):
    global is_cooling_down
    
    # If another thread triggered a cool-down, wait here
    while is_cooling_down:
        time.sleep(2)

    session = get_session()
    search_word = spaced_root.replace(" ", "")
    url = f"https://www.almaany.com/en/dict/ar-en/{search_word}/"
    
    # A slightly wider jitter window to protect the IP
    time.sleep(random.uniform(1.2, 2.8))
    
    try:
        response = session.get(url, timeout=12)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results_div = soup.find('div', class_='panel-body')
            
            if results_div:
                raw_text = results_div.get_text(separator='\n')
                clean_text = '\n'.join([line.strip() for line in raw_text.split('\n') if line.strip()])
                return (spaced_root, clean_text, None)
            else:
                return (spaced_root, "No deep dive available.", None)
                
        elif response.status_code in [403, 429]:
            with global_lock:
                if not is_cooling_down:
                    is_cooling_down = True
                    print(f"\n🛑 [!] Rate limit hit (HTTP {response.status_code}). Initiating a 45-second IP cool-down...")
                    time.sleep(45)
                    is_cooling_down = False
            return (spaced_root, None, "RETRY")
        else:
            return (spaced_root, None, f"HTTP {response.status_code}")
            
    except Exception as e:
        return (spaced_root, None, str(e))

def scrape_almaany():
    conn = sqlite3.connect(DB_NAME, timeout=15)
    cursor = conn.cursor()
    setup_database(cursor)
    
    cursor.execute("SELECT root_arabic FROM roots WHERE almaany_en IS NULL OR almaany_en = ''")
    pending_roots = [row[0] for row in cursor.fetchall()]
    
    if not pending_roots:
        print("🎉 Database is fully enriched!")
        conn.close()
        return

    print(f"🎯 Starting Stealth Backoff Scraper for {len(pending_roots)} roots...")
    
    added = 0
    total_processed = 0
    batch_data = []

    # Dropped down to 2 workers to keep request patterns more discrete
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(fetch_almaany, root): root for root in pending_roots}
        
        while futures:
            done_futures = []
            for future in list(futures.keys()):
                if future.done():
                    done_futures.append(future)
                    total_processed += 1
                    spaced_root, clean_text, error = future.result()
                    search_word = spaced_root.replace(" ", "")
                    
                    if error == "RETRY":
                        # Re-submit the word to the back of the line so we don't skip it
                        new_future = executor.submit(fetch_almaany, spaced_root)
                        futures[new_future] = spaced_root
                        total_processed -= 1  # Adjust count
                        continue
                        
                    if error:
                        print(f"   [!] Error on '{search_word}': {error}")
                        continue
                        
                    batch_data.append((clean_text, spaced_root))
                    added += 1
                    
                    if len(batch_data) >= 10:  # Smaller batch commits for visibility
                        cursor.executemany("UPDATE roots SET almaany_en = ? WHERE root_arabic = ?", batch_data)
                        conn.commit()
                        print(f"   ⚡ Scraped... [{total_processed}/{len(pending_roots)}] | Saved: {search_word}")
                        batch_data = []
            
            for f in done_futures:
                del futures[f]
            time.sleep(0.5)
                
    if batch_data:
        cursor.executemany("UPDATE roots SET almaany_en = ? WHERE root_arabic = ?", batch_data)
        conn.commit()

    conn.close()
    print("\n========================================")
    print(f"🚀 SCRAPING RUN COMPLETE! Added {added} entries.")
    print("========================================")

if __name__ == "__main__":
    scrape_almaany()
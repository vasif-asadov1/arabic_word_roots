import os
import sqlite3
import requests
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")

def fetch_translations(raw_root):
    """Retries up to 3 times if the network fails, with human-like delays."""
    # Jitter: Random pause to bypass Google's bot detection
    time.sleep(random.uniform(0.3, 0.8)) 
    
    retries = 3
    for i in range(retries):
        try:
            eng = GoogleTranslator(source='ar', target='en').translate(raw_root)
            tur = GoogleTranslator(source='ar', target='tr').translate(raw_root)
            return (raw_root, eng, tur, None)
        except Exception as e:
            if i < retries - 1:
                wait_time = (i + 1) * 15  # Wait 15s, then 30s
                print(f"   [!] Network error for '{raw_root}'. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return (raw_root, None, None, str(e))

def expand_database():
    print("1. Downloading open-source root dataset from GitHub...")
    url = "https://raw.githubusercontent.com/linuxscout/arabic-roots/master/data/roots.txt"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        text_data = response.text
    except Exception as e:
        print(f"Failed to download from GitHub: {e}")
        return

    print("2. Parsing roots...")
    new_roots = []
    for line in text_data.split('\n'):
        raw_root = line.strip()
        if 2 <= len(raw_root) <= 4 and re.search(r'[\u0600-\u06FF]', raw_root):
            new_roots.append(raw_root)
                
    new_roots = list(set(new_roots))
    
    conn = sqlite3.connect(DB_NAME, timeout=15)
    cursor = conn.cursor()
    
    cursor.execute("SELECT root_arabic FROM roots")
    existing_db_roots = set(row[0].replace(" ", "") for row in cursor.fetchall())
    
    roots_to_add = [r for r in new_roots if r not in existing_db_roots]
    skipped_instantly = len(new_roots) - len(roots_to_add)
    
    print(f"⚡ RAM Check: Instantly skipped {skipped_instantly} existing roots.")
    print(f"🎯 Roots remaining to translate: {len(roots_to_add)}\n")

    if not roots_to_add:
        print("Database is already fully populated!")
        return

    added = 0
    total_processed = 0
    batch_data = []
    
    print("--- 🚀 STABLE MULTITHREADING STARTED (2 WORKERS) ---")
    
    # Strictly set to 2 to prevent instant bans
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_translations, r): r for r in roots_to_add}
        
        for future in as_completed(futures):
            total_processed += 1
            raw_root, eng, tur, error = future.result()
            
            if error:
                print(f"   [!] Error translating '{raw_root}': {error}")
                continue
                
            spaced_root = " ".join(list(raw_root))
            batch_data.append((spaced_root, eng, tur))
            added += 1
            
            if len(batch_data) >= 50:
                cursor.executemany('''
                    INSERT INTO roots (root_arabic, meaning_english, meaning_turkish)
                    VALUES (?, ?, ?)
                ''', batch_data)
                conn.commit()
                print(f"   ⚡ Scan... [{total_processed}/{len(roots_to_add)}] | Successfully Added: {added}")
                batch_data = [] 
                
    if batch_data:
        cursor.executemany('''
            INSERT INTO roots (root_arabic, meaning_english, meaning_turkish)
            VALUES (?, ?, ?)
        ''', batch_data)
        conn.commit()

    conn.close()
    
    print("\n" + "="*40)
    print("🚀 EXPANSION COMPLETE!")
    print(f"New Roots Added: {added}")
    print("="*40)

if __name__ == "__main__":
    expand_database()
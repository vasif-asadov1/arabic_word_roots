import os
import sqlite3
import requests
from deep_translator import GoogleTranslator
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")

def build_pipeline():
    print("1. API limit bypassed. Downloading raw JSON directly from the repository CDN...")
    
    # Direct raw link to the dataset (bypasses GitHub API limits completely)
    raw_url = "https://raw.githubusercontent.com/R3GENESI5/quran-bil-quran/master/app/data/roots_index.json"
    
    response = requests.get(raw_url)
    if response.status_code != 200:
        print("Could not download the raw file. Check your internet connection.")
        return

    data = response.json()
    print(f"2. Loaded {len(data)} roots! Translating English to Turkish and injecting into SQLite...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    translator = GoogleTranslator(source='en', target='tr')
    
    added = 0
    
    # The JSON is structured as { "كتب": { "m": "meaning...", ... } }
    for root, details in data.items():
        arabic_root = str(root).strip()
        
        # Extract the meaning (checking common keys in case the schema varies slightly)
        english_meaning = details.get('m', details.get('meaning', details.get('gloss', '')))
        
        # Fallback: if meaning is empty, grab the longest text string from the dictionary
        if not english_meaning:
            string_vals = [str(v) for v in details.values() if isinstance(v, str)]
            if string_vals:
                english_meaning = max(string_vals, key=len)
            else:
                continue 
                
        # Format root with spaces to match our UI aesthetic (e.g., كتب -> ك ت ب)
        if len(arabic_root) == 3 and " " not in arabic_root:
            arabic_root = " ".join(list(arabic_root))
            
        # Prevent duplicates
        cursor.execute("SELECT COUNT(*) FROM roots WHERE root_arabic = ?", (arabic_root,))
        if cursor.fetchone()[0] == 0:
            try:
                # Real-time translation to Turkish
                turkish_meaning = translator.translate(english_meaning)
                
                cursor.execute('''
                    INSERT INTO roots (root_arabic, meaning_english, meaning_turkish)
                    VALUES (?, ?, ?)
                ''', (arabic_root, english_meaning, turkish_meaning))
                added += 1
                
                if added % 50 == 0:
                    print(f"   ✓ Processed & translated {added} roots...")
                    conn.commit()
                    
                time.sleep(0.1) # Small delay to respect Google Translate servers
            except Exception as e:
                pass # Skip problematic rows silently
                
    conn.commit()
    conn.close()
    print(f"Pipeline Complete! Successfully injected {added} translated roots into your database.")

if __name__ == "__main__":
    build_pipeline()
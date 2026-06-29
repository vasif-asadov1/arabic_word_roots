import os
import sqlite3
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_DB = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")
LANE_DB = os.path.join(BASE_DIR, "..", "data", "lexicon.sqlite")

def clean_xml_tags(text):
    """Simple regex to remove XML tags and leave clean text."""
    if not text:
        return ""
    # This removes everything between < and >
    return re.sub(r'<[^>]+>', ' ', text)

def merge_lexicon():
    print("🚀 Connecting to databases...")
    conn = sqlite3.connect(MY_DB)
    cursor = conn.cursor()
    
    # ATTACH the Lexicon database
    cursor.execute(f"ATTACH DATABASE '{LANE_DB}' AS lanes")
    
    print("🔍 Fetching Lane's Lexicon entries...")
    # Fetch all entries from the attached database
    cursor.execute("SELECT root, xml FROM lanes.entry")
    lexicon_data = cursor.fetchall()
    
    print(f"📦 Found {len(lexicon_data)} entries. Merging into your database...")
    
    # We will use a dictionary for fast lookup
    lexicon_map = {row[0]: clean_xml_tags(row[1]) for row in lexicon_data}
    
    # Get all your roots
    cursor.execute("SELECT root_arabic FROM roots")
    my_roots = cursor.fetchall()
    
    batch_data = []
    for row in my_roots:
        root = row[0]
        # Remove spaces to match Lane's root format (e.g., "ك ت ب" -> "كتب")
        search_root = root.replace(" ", "")
        
        if search_root in lexicon_map:
            batch_data.append((lexicon_map[search_root], root))
            
    # Batch update your database
    if batch_data:
        cursor.executemany("""
            UPDATE roots 
            SET almaany_en = ? 
            WHERE root_arabic = ?
        """, batch_data)
        conn.commit()
        print(f"🎉 SUCCESS! Merged {len(batch_data)} deep definitions.")
    else:
        print("⚠️ No matching roots found. Check if your root format matches Lane's.")
    
    conn.close()

if __name__ == "__main__":
    if not os.path.exists(LANE_DB):
        print(f"❌ Error: {LANE_DB} not found!")
    else:
        merge_lexicon()
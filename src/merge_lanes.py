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
    return re.sub(r'<[^>]+>', ' ', text)

def merge_lexicon_fixed():
    print("🚀 Re-merging Lane's Lexicon (Fetching ALL entries per root)...")
    conn = sqlite3.connect(MY_DB)
    cursor = conn.cursor()
    
    # ATTACH the Lexicon database
    cursor.execute(f"ATTACH DATABASE '{LANE_DB}' AS lanes")
    
    # --- THE FIX: GROUP_CONCAT ---
    # This stitches every single row for a root together, separated by '-b2-' 
    # so your DeepDiveDialog parser automatically turns them into separate bullet points!
    cursor.execute("""
        SELECT root, GROUP_CONCAT(xml, ' -b2- ') as combined_xml
        FROM lanes.entry
        GROUP BY root
    """)
    lexicon_data = cursor.fetchall()
    
    print(f"📦 Aggregated {len(lexicon_data)} complete root families. Overwriting old data...")
    
    lexicon_map = {row[0]: clean_xml_tags(row[1]) for row in lexicon_data}
    
    cursor.execute("SELECT root_arabic FROM roots")
    my_roots = cursor.fetchall()
    
    batch_data = []
    for row in my_roots:
        root = row[0]
        search_root = root.replace(" ", "")
        
        if search_root in lexicon_map:
            # We overwrite whatever was there previously with the full aggregated block
            batch_data.append((lexicon_map[search_root], root))
            
    if batch_data:
        cursor.executemany("""
            UPDATE roots 
            SET almaany_en = ? 
            WHERE root_arabic = ?
        """, batch_data)
        conn.commit()
        print(f"🎉 FIXED! Successfully saved massive, full definitions for {len(batch_data)} roots.")
    
    conn.close()

if __name__ == "__main__":
    merge_lexicon_fixed()
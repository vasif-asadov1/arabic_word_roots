import sqlite3
import os
from sarf_engine import SarfEngine

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")
OUTPUT_HTML = os.path.join(BASE_DIR, "..", "data", "arabic_study_guide.html")

def generate_html_guide():
    print("🚀 Connecting to database...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Grab only the first 2000 roots
    cursor.execute("SELECT root_arabic, meaning_english, meaning_turkish FROM roots LIMIT 2000")
    roots_data = cursor.fetchall()
    conn.close()

    if not roots_data:
        print("❌ No data found!")
        return

    print(f"📦 Loaded {len(roots_data)} roots. Spinning up Sarf Engine...")
    engine = SarfEngine()
    
    # HTML Setup with beautiful print-optimized CSS
    html_content = [
        "<!DOCTYPE html>",
        "<html lang='tr'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<title>Arabic Roots Study Guide</title>",
        "<style>",
        "  @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;600&display=swap');",
        "  body { font-family: 'Inter', sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 20px; }",
        "  .container { max-width: 800px; margin: 0 auto; }",
        "  .header { text-align: center; padding: 40px 0; border-bottom: 3px solid #4a6984; margin-bottom: 40px; }",
        "  .header h1 { font-family: 'Amiri', serif; font-size: 54px; margin: 0; color: #1e3a4a; }",
        "  .header p { font-size: 18px; color: #6c757d; }",
        "  .word-card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); page-break-inside: avoid; }",
        "  /* 🔥 MASSIVE ARABIC ROOT FONT */",
        "  .root-title { font-family: 'Amiri', serif; font-size: 64px; font-weight: bold; color: #2b2b2b; text-align: center; margin: 0 0 10px 0; direction: rtl; line-height: 1.2; }",
        "  .meanings { text-align: center; margin-bottom: 25px; font-size: 16px; }",
        "  .meanings .tr { font-weight: bold; color: #c92a2a; font-size: 18px;} ",
        "  .meanings .en { color: #5c5c5c; }",
        "  table { width: 100%; border-collapse: collapse; margin-top: 15px; }",
        "  th, td { padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6; font-size: 15px; vertical-align: middle; }",
        "  th { background-color: #f1f3f5; font-weight: 600; color: #495057; }",
        "  /* 🔥 MASSIVE CONJUGATION FONT + LINE HEIGHT FOR VOWELS */",
        "  .arabic-cell { font-family: 'Amiri', serif; font-size: 34px; direction: rtl; color: #1e3a4a; font-weight: bold; line-height: 1.6; padding: 15px 10px; }",
        "  .zamir-cell { font-weight: 600; color: #343a40; text-align: left; padding-left: 20px; width: 25%; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='container'>",
        "<div class='header'>",
        "  <h1>أصل الكلمة</h1>",
        "  <p>Fusha Arabic Roots — Top 2000 Comprehensive Study Guide</p>",
        "</div>"
    ]

    print("⚙️ Conjugating 2,000 words... (This will take a few seconds)")
    
    # Generate the cards
    for idx, (root, eng, tur) in enumerate(roots_data):
        html_content.append("<div class='word-card'>")
        html_content.append(f"<div class='root-title'>{root}</div>")
        html_content.append(f"<div class='meanings'><span class='tr'>🇹🇷 {tur}</span><br><span class='en'>🇬🇧 {eng}</span></div>")
        
        # Conjugation Table
        html_content.append("<table>")
        html_content.append("<tr><th>Zamir (Kişi)</th><th>Geçmiş Zaman (Madi)</th><th>Şimdiki Zaman (Mudari)</th></tr>")
        
        for zamir in engine.past_suffixes.keys():
            madi = engine.conjugate_past_tense(root, zamir)
            mudari = engine.conjugate_present_tense(root, zamir)
            
            # Formatting the Zamir string slightly for better print readability
            clean_zamir = zamir.replace(" (", "<br><span style='font-size: 12px; color: #868e96;'>(").replace(")", ")</span>")
            
            html_content.append("<tr>")
            html_content.append(f"<td class='zamir-cell'>{clean_zamir}</td>")
            html_content.append(f"<td class='arabic-cell'>{madi if madi != 'Error' else '-'}</td>")
            html_content.append(f"<td class='arabic-cell'>{mudari if mudari != 'Error' else '-'}</td>")
            html_content.append("</tr>")
            
        html_content.append("</table>")
        html_content.append("</div>")

        if (idx + 1) % 500 == 0:
            print(f"   ... Processed {idx + 1} / 2000 roots")

    html_content.append("</div></body></html>")

    print(f"💾 Saving to {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print("\n==================================================")
    print("🎉 SUCCESS! HTML Guide Generated.")
    print(f"File saved at: {OUTPUT_HTML}")
    print("To get your PDF: Open this HTML file in Chrome/Brave, press Ctrl+P, and select 'Save as PDF'.")
    print("==================================================")

if __name__ == "__main__":
    generate_html_guide()
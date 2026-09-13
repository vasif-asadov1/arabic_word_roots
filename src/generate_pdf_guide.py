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
    
    # Grab only the first 6000 roots
    cursor.execute("SELECT root_arabic, meaning_english, meaning_turkish FROM roots LIMIT 6000")
    roots_data = cursor.fetchall()
    conn.close()

    if not roots_data:
        print("❌ No data found!")
        return

    print(f"📦 Loaded {len(roots_data)} roots. Spinning up Sarf Engine...")
    engine = SarfEngine()
    
    # HTML Setup with beautiful print-optimized CSS and Master Guide styles
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
        "  .guide-section { background: white; border-radius: 8px; padding: 30px; margin-bottom: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }",
        "  .guide-section h2 { color: #1e3a4a; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; font-size: 24px; }",
        "  .guide-section h3 { color: #4a6984; margin-top: 30px; font-size: 20px; }",
        "  .guide-text { font-size: 16px; line-height: 1.6; color: #495057; }",
        "  .math-box { background: #e9ecef; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 16px; margin: 15px 0; border-left: 4px solid #88c0d0; color: #212529; font-weight: 600; }",
        "  .page-break { page-break-after: always; }",
        "  .word-card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); page-break-inside: avoid; border-left: 6px solid #4a6984; }",
        "  .root-title { font-family: 'Amiri', serif; font-size: 64px; font-weight: bold; color: #2b2b2b; text-align: center; margin: 0 0 10px 0; direction: rtl; line-height: 1.2; }",
        "  .meanings { text-align: center; margin-bottom: 25px; font-size: 16px; }",
        "  .meanings .tr { font-weight: bold; color: #c92a2a; font-size: 18px;} ",
        "  .meanings .en { color: #5c5c5c; }",
        "  table { width: 100%; border-collapse: collapse; margin-top: 15px; }",
        "  th, td { padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6; font-size: 15px; vertical-align: middle; }",
        "  th { background-color: #f1f3f5; font-weight: 600; color: #495057; }",
        "  .arabic-cell { font-family: 'Amiri', serif; font-size: 34px; direction: rtl; color: #1e3a4a; font-weight: bold; line-height: 1.6; padding: 15px 10px; }",
        "  .zamir-cell { font-weight: 600; color: #343a40; text-align: left; padding-left: 20px; width: 25%; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class='container'>",
        
        # --- MASTER GUIDE SECTION ---
        "<div class='header'>",
        "  <h1>أصل الكلمة</h1>",
        "  <p>Fusha Arabic Roots — The Master Guide & Top 2000 Lexicon</p>",
        "</div>",
        "<div class='guide-section'>",
        "  <h2>The Mathematical Logic of Arabic Morphology (Sarf)</h2>",
        "  <p class='guide-text'>Arabic is built on a highly mathematical system of 3-letter roots. By mastering core suffixes and prefixes, you can derive any pronoun form without memorizing thousands of separate words. This dictionary uses the professional academic standard: displaying only the <b>3rd Person Masculine Singular (Hüve)</b> base form. Use the formulas below to unlock the remaining pronouns.</p>",
        "  ",
        "  <h3>1. Geçmiş Zaman (Madi) - The Past Tense</h3>",
        "  <p class='guide-text'>The past tense is created strictly by adding <b>suffixes</b> to the end of the root letters (L1, L2, L3).</p>",
        "  <div class='math-box'>Formula: L1(Fatha) + L2(Fatha) + L3 + [SUFFIX]</div>",
        "  ",
        "  <h3>2. Şimdiki/Geniş Zaman (Mudari) - The Present Tense</h3>",
        "  <p class='guide-text'>The present tense requires a <b>prefix</b> before the root, places a <i>sukun</i> (stop) on the first root letter, and sometimes adds a <b>suffix</b>.</p>",
        "  <div class='math-box'>Formula: [PREFIX] + L1(Sukun) + L2(Damma) + L3 + [SUFFIX]</div>",
        "  ",
        "  <h3>Master Reference Table: ك ت ب (To Write)</h3>",
        "  <table>",
        "  <tr><th>Zamir (Kişi)</th><th>Geçmiş Zaman (Madi)</th><th>Şimdiki Zaman (Mudari)</th></tr>"
    ]

    # Generate the 14-row Master Table dynamically using your engine
    test_root = "ك ت ب"
    for zamir in engine.past_suffixes.keys():
        madi = engine.conjugate_past_tense(test_root, zamir)
        mudari = engine.conjugate_present_tense(test_root, zamir)
        clean_zamir = zamir.replace(" (", "<br><span style='font-size: 12px; color: #868e96;'>(").replace(")", ")</span>")
        
        html_content.append("<tr>")
        html_content.append(f"<td class='zamir-cell'>{clean_zamir}</td>")
        html_content.append(f"<td class='arabic-cell'>{madi}</td>")
        html_content.append(f"<td class='arabic-cell'>{mudari}</td>")
        html_content.append("</tr>")

    html_content.append("  </table>")
    html_content.append("</div>")
    
    # Force the dictionary to start on a fresh page in the PDF
    html_content.append("<div class='page-break'></div>")
    # --- END MASTER GUIDE SECTION ---

    print("⚙️ Conjugating 6,000 dictionary base forms...")
    
    # Generate the condensed word cards
    for idx, (root, eng, tur) in enumerate(roots_data):
        html_content.append("<div class='word-card'>")
        html_content.append(f"<div class='root-title'>{root}</div>")
        html_content.append(f"<div class='meanings'><span class='tr'>🇹🇷 {tur}</span><br><span class='en'>🇬🇧 {eng}</span></div>")
        
        # Condensed Table (Hüve Form Only)
        html_content.append("<table>")
        html_content.append("<tr><th>Zamir (Kişi)</th><th>Geçmiş Zaman (Madi)</th><th>Şimdiki Zaman (Mudari)</th></tr>")
        
        base_zamir = "O [E] (Hüve)"
        madi = engine.conjugate_past_tense(root, base_zamir)
        mudari = engine.conjugate_present_tense(root, base_zamir)
        
        html_content.append("<tr>")
        html_content.append(f"<td class='zamir-cell'>O [E]<br><span style='font-size: 12px; color: #868e96;'>(Hüve - Base Form)</span></td>")
        html_content.append(f"<td class='arabic-cell'>{madi if madi != 'Error' else '-'}</td>")
        html_content.append(f"<td class='arabic-cell'>{mudari if mudari != 'Error' else '-'}</td>")
        html_content.append("</tr>")
            
        html_content.append("</table>")
        html_content.append("</div>")

        if (idx + 1) % 500 == 0:
            print(f"   ... Processed {idx + 1} / 6000 roots")

    html_content.append("</div></body></html>")

    print(f"💾 Saving to {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print("\n==================================================")
    print("🎉 SUCCESS! Condensed Dictionary & Master Guide Generated.")
    print("==================================================")

if __name__ == "__main__":
    generate_html_guide()
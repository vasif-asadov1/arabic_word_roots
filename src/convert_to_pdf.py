import os
from playwright.sync_api import sync_playwright

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "..", "data", "arabic_study_guide.html")
PDF_FILE = os.path.join(BASE_DIR, "..", "data", "arabic_study_guide.pdf")

def convert_html_to_pdf():
    if not os.path.exists(HTML_FILE):
        print(f"❌ Could not find {HTML_FILE}. Run generate_pdf_guide.py first!")
        return

    print("🚀 Spinning up Headless Chrome Engine...")
    
    with sync_playwright() as p:
        # Launch Chromium silently in the background
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("📄 Loading the HTML masterpiece...")
        # Point the browser to your local HTML file
        file_url = f"file://{os.path.abspath(HTML_FILE)}"
        
        # wait_until="networkidle" ensures Google Fonts (Amiri, Inter) are fully downloaded before printing
        page.goto(file_url, wait_until="networkidle")
        
        print("🖨️  Rendering PDF (this might take 10-20 seconds for 2,000 words)...")
        # Generate the PDF with perfect print settings
        page.pdf(
            path=PDF_FILE,
            format="A4",
            print_background=True,  # Keeps your beautiful table header colors
            margin={"top": "40px", "right": "20px", "bottom": "40px", "left": "20px"}
        )
        
        browser.close()
        
    print("\n==================================================")
    print("🎉 ABSOLUTE PERFECTION! PDF Generated.")
    print(f"File saved at: {PDF_FILE}")
    print("==================================================")

if __name__ == "__main__":
    convert_html_to_pdf()
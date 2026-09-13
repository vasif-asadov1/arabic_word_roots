from playwright.sync_api import sync_playwright

def test_almaany():
    with sync_playwright() as p:
        print("🚀 Spinning up Chrome browser...")
        # Add arguments to try and hide the automation flags from Cloudflare
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        # Remove the webdriver flag via JavaScript injection before the page loads
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        test_word = "كتب"
        print(f"🎯 Navigating to Almaany for the root: {test_word}...")
        
        try:
            # FIX 1: Change to domcontentloaded so it doesn't wait for the network
            page.goto(f"https://www.almaany.com/en/dict/ar-en/{test_word}/", wait_until="domcontentloaded")
            
            # FIX 2: Give you 60 full seconds to click the CAPTCHA
            print("⏳ Waiting up to 60 seconds... If you see a CAPTCHA, solve it now!")
            page.wait_for_selector("div.panel-body", timeout=60000)
            
            raw_text = page.locator("div.panel-body").first.inner_text()
            clean_text = '\n'.join([line.strip() for line in raw_text.split('\n') if line.strip()])
            
            print("\n✅ SUCCESS! Cloudflare bypassed. Extracted Data:\n")
            print("="*40)
            print(clean_text[:400] + "\n... [TRUNCATED] ...")
            print("="*40)
            
        except Exception as e:
            print(f"\n❌ BLOCKED: The firewall won. Error: {e}")
            
        finally:
            print("\n🛑 Closing browser...")
            browser.close()

if __name__ == "__main__":
    test_almaany()
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError

load_dotenv()

SP_USERNAME = os.getenv("SP_USERNAME")
SP_PASSWORD = os.getenv("SP_PASSWORD")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://hub.servicepower.com/signin", timeout=30000)
            page.screenshot(path="page_loaded.png")

            page.fill('input[name="username"]', SP_USERNAME)
            page.fill('input[name="password"]', SP_PASSWORD)
            page.click('button[type="submit"]')

            page.wait_for_load_state("networkidle")
            page.screenshot(path="after_login.png")
            print("✅ Login attempted")

            # Optional: check if login was successful
            if "dashboard" in page.url or "home" in page.url:
                print("🎉 Logged in successfully!")
            else:
                print("⚠️ Login may not have worked. Check screenshot.")

        except TimeoutError:
            print("❌ Timeout loading page")
        except Exception as e:
            print("❌ Login failed:", type(e).__name__, "-", str(e))
        finally:
            browser.close()

if __name__ == "__main__":
    main()

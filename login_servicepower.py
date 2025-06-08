from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

SP_USERNAME = os.getenv("SP_USERNAME")
SP_PASSWORD = os.getenv("SP_PASSWORD")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(options=chrome_options)

def main():
    driver = get_driver()

    try:
        driver.get("https://hub.servicepower.com/signin")

        # 🔍 Save a screenshot of the login page (for debugging)
        driver.save_screenshot("login_page.png")

        print(driver.page_source[:1000])  # print first 1000 characters of HTML

        # ✅ Wait for login fields
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "login"))
        )

        # ✍️ Fill in credentials
        driver.find_element(By.ID, "username").send_keys(SP_USERNAME)
        driver.find_element(By.ID, "password").send_keys(SP_PASSWORD)
        driver.find_element(By.ID, "login").click()

        print("✅ Login attempted successfully.")

        # 🧠 Optional: wait for some post-login indicator
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        print("🎉 Logged in and dashboard loaded.")

    except Exception as e:
        # 🛠 Log the actual error type and save screenshot
        print("❌ Login failed:", type(e).__name__, "-", str(e))
        driver.save_screenshot("error_debug.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

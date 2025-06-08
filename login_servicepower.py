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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def main():
    driver = get_driver()

    try:
        driver.get("https://www.servicepower.com/login")  # Replace with actual login URL

        # Wait for username field
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        # Wait for password field
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        # Wait for login button
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "login"))
        )

        # Fill in and submit login form
        driver.find_element(By.ID, "username").send_keys(SP_USERNAME)
        driver.find_element(By.ID, "password").send_keys(SP_PASSWORD)
        driver.find_element(By.ID, "login").click()

        print("✅ Login attempted successfully.")

        # Optional: wait for successful login confirmation (adjust selector)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "dashboard"))  # Example ID
        )
        print("🎉 Logged in and dashboard loaded.")

    except Exception as e:
        print("❌ Login failed:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

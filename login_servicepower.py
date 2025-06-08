import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()  # load SP_USERNAME and SP_PASSWORD

SP_USERNAME = os.environ.get("SP_USERNAME")
SP_PASSWORD = os.environ.get("SP_PASSWORD")

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://hub.servicepower.com/signin")

    # Replace these selectors with actual ones from the login page
    driver.find_element(By.ID, "username").send_keys(SP_USERNAME)
    driver.find_element(By.ID, "password").send_keys(SP_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]").click()

    driver.implicitly_wait(10)
    title = driver.title
    print(f"Page title after login: {title}")

    orders_exists = bool(driver.find_elements(By.LINK_TEXT, "Work Orders"))
    print("Work Orders section found:", orders_exists)

    driver.quit()

if __name__ == "__main__":
    main()

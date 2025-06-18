from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import json
import os
import time

SP_USERNAME = "support@prostarapp.com"
SP_PASSWORD = "Prostar2024!"
HCP_API_KEY = "e9e62417edae40199420a6c54b71657c"
SYNC_LOG_FILE = "synced_orders.json"

OFFICE_STATE_MAP = {
    "ProStar Jacksonville": "FL",
    "ProStar DFW": "TX",
    "ProStar Phoenix": "AZ",
    # Add more mappings if needed
}

def load_synced_ids():
    if os.path.exists(SYNC_LOG_FILE):
        with open(SYNC_LOG_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_synced_ids(ids):
    with open(SYNC_LOG_FILE, "w") as f:
        json.dump(list(ids), f)

def extract_from_cells(cells):
    return [cell.inner_text().strip() for cell in cells]

def create_customer(data):
    response = requests.post(
        "https://api.housecallpro.com/customers",
        headers={
            "Authorization": f"Bearer {HCP_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )
    if response.status_code == 201:
        return response.json().get("id")
    print("❌ Failed to create customer:", response.status_code, response.text)
    return None

def create_address(customer_id, data):
    response = requests.post(
        f"https://api.housecallpro.com/customers/{customer_id}/addresses",
        headers={
            "Authorization": f"Bearer {HCP_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )
    return response.json().get("id") if response.status_code == 201 else None

def create_job(data):
    response = requests.post(
        "https://api.housecallpro.com/jobs",
        headers={
            "Authorization": f"Bearer {HCP_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )
    print("💪 Job creation response:", response.status_code, response.text)

def main():
    print("🎮 Launching browser...")
    synced_ids = load_synced_ids()
    new_synced = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("🔐 Navigating to ServicePower...")
            page.goto("https://hub.servicepower.com/signin", timeout=60000)

            print("⏳ Logging in...")
            page.wait_for_selector("#email", timeout=15000)
            page.fill("#email", SP_USERNAME)
            page.fill("input[name='password']", SP_PASSWORD)
            page.click("button.btn-primary:has-text('Sign In')")
            print("🔄 Waiting for dashboard to load...")
            page.wait_for_load_state("networkidle", timeout=45000)
            print("✅ Logged in successfully.")

            print("📁 Navigating to Work Orders page...")
            try:
                orders_menu = page.locator("text=Orders").first
                orders_menu.hover()
                time.sleep(1)
                submenu = page.locator("a[href='/orders/work-order-list']")
                submenu.wait_for(state="visible", timeout=10000)
                submenu.click()
            except:
                print("⚠️ Fallback: clicking menu")
                page.locator("text=Orders").click()
                page.locator("a[href='/orders/work-order-list']").click()

            page.wait_for_selector("table tbody tr", timeout=20000)
            print("✅ Work Orders page loaded.")

            rows = page.query_selector_all("table tbody tr")
            print(f"🔎 Found {len(rows)} work orders on the page.")

            for row in rows:
                cells = row.query_selector_all("td")
                cell_data = extract_from_cells(cells)

                if len(cell_data) < 6:
                    continue

                work_order_id = cell_data[1].replace("Work Order #", "").strip()
                if work_order_id in synced_ids or "accepted" not in cell_data[3].lower():
                    continue

                print(f"📄 Processing W/O {work_order_id}...")

                name = f"{cell_data[6]} {cell_data[7]}"
                phone = ""
                email = ""
                address = ""
                city = cell_data[14]
                zip_code = cell_data[15]
                appointment = cell_data[11]
                description = cell_data[9]
                office_name = cell_data[13]
                state = OFFICE_STATE_MAP.get(office_name, "")

                if not (city and zip_code and state):
                    print("⚠️ Incomplete address data.")
                    continue

                first_name, *last_name = name.split()
                last_name = " ".join(last_name) if last_name else ""

                print("👤 Creating new customer...")
                customer_id = create_customer({
                    "first_name": f"{first_name} ({work_order_id})",
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "notes": f"Work Order ID: {work_order_id}\nAppointment: {appointment}\nProblem: {description}"
                })

                if not customer_id:
                    continue

                print("📦 Adding address...")
                address_id = create_address(customer_id, {
                    "street": f"{city}, {state}",
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "country": "US",
                    "is_default": True
                })

                print("🛠️ Creating job...")
                create_job({
                    "customer_id": customer_id,
                    "address_id": address_id,
                    "job_description": f"Auto-imported from ServicePower W/O {work_order_id}",
                    "status": "unscheduled",
                    "line_items": [
                        {"type": "service", "name": "Imported Job", "price": 120}
                    ]
                })

                new_synced.add(work_order_id)

        except Exception as e:
            print("❌ Error:", str(e))
        finally:
            print("🪟 Closing browser...")
            browser.close()
            synced_ids.update(new_synced)
            save_synced_ids(synced_ids)

if __name__ == "__main__":
    main()

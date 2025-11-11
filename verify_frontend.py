from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto("http://localhost:8000/users/accounts/login/")
        page.wait_for_load_state("networkidle")
        page.fill('input[name="username"]', "admin@example.com")
        page.fill('input[name="password"]', "admin")
        page.click('button[type="submit"]')

        # Wait for navigation to the admin page and then go to the home page
        page.wait_for_url("http://localhost:8000/admin/")
        page.goto("http://localhost:8000/")

        # Wait for the chatbot widget to be visible
        time.sleep(5)
        page.wait_for_selector("#chatbot-widget", state="visible", timeout=30000)
        print("Chatbot widget found.")

        # Take a screenshot
        page.screenshot(path="chatbot-widget.png")
        print("Screenshot taken.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)

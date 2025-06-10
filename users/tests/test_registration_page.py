import re
from playwright.sync_api import Playwright, sync_playwright, expect
import pytest
from playwright.sync_api import Page, expect # Import expect for Playwright's assertions

BASE_URL = "http://localhost:8000" # Good practice


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")
    page.get_by_role("link", name="Register").click()
    page.get_by_role("textbox", name="First name*").click()
    page.get_by_role("textbox", name="First name*").fill("First")
    page.get_by_role("textbox", name="First name*").press("Tab")
    page.get_by_role("textbox", name="Last name*").fill("Last")
    page.get_by_role("textbox", name="Last name*").press("Tab")
    page.get_by_role("textbox", name="Email*").fill("mail22@mail.com")
    page.get_by_role("textbox", name="Email*").press("Tab")
    page.get_by_role("textbox", name="Password*").fill("Password25!")
    page.get_by_role("textbox", name="Wedding day").fill("2025-06-10")
    page.get_by_role("button", name="Register").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

# tests/test_e2e_homepage.py

# Make sure your Django development server is running before executing this test.
# You typically run `python manage.py runserver` in a separate terminal.

BASE_URL = "http://localhost:8000" # Or whatever your dev server runs on

def test_homepage_has_correct_title(page):
    """
    Tests if the homepage loads and has the expected title.
    The 'page' fixture is provided by pytest-playwright.
    """
    page.goto(BASE_URL + "/")
    # You can use Playwright's powerful locators and assertions
    # For a simple title check:
    assert "Welcome to V planner" in page.title(), f"Expected 'Welcome to V planner' in title, but got '{page.title()}'"
    print(f"Page title is: {page.title()}") # Optional: for seeing output


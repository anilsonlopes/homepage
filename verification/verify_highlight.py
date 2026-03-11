from playwright.sync_api import sync_playwright
import os

def verify_word_highlight(page):
    page.goto("http://localhost:4173/")
    page.wait_for_selector("main")

    print("Main content:")
    print(page.locator("main").inner_html())

    page.screenshot(path="verification/initial_state.png")

    first_highlight = page.locator("mark").first
    first_highlight.hover()

    page.screenshot(path="verification/hover_state.png")

    first_highlight.focus()

    page.screenshot(path="verification/focus_state.png")

if __name__ == "__main__":
    os.makedirs("verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_word_highlight(page)
            print("Verification script ran successfully.")
        finally:
            browser.close()
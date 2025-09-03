from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time

from .config import WAIT_TIMEOUT

class MainPage:
    def __init__(self, driver, wait=None):
        self.driver = driver
        self.wait = wait or WebDriverWait(driver, WAIT_TIMEOUT,
                                          ignored_exceptions=(StaleElementReferenceException,))

    def open(self, url):
        self.driver.get(url)
        self.wait.until(lambda d: (d.title or "") != "")
        return self

    def _find_chat_input(self):
        # Try common options; adapt if UI switches input element type
        return self.wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "textarea[name='message'], input[name='message'], textarea"
        )))

    def enter_message(self, message):
        chat_input = self._find_chat_input()
        chat_input.clear()
        chat_input.send_keys(message)
        return self

    def send_message(self):
        # Click submit if present; otherwise press Enter in the field
        try:
            btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form button[type='submit']")))
            btn.click()
        except TimeoutException:
            # Fallback: press Enter in the input
            chat_input = self._find_chat_input()
            chat_input.send_keys(Keys.ENTER)
        return self

    def _latest_nonempty_text(self, driver, selector_list):
        sel = ", ".join(selector_list)
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        for el in reversed(els):
            try:
                txt = el.text.strip()
            except Exception:
                txt = ""
            if txt:
                return txt
        return False

    def wait_for_user_bubble(self, expected_substring=None):
        # Right/user side: sometimes tailwind uses self-end or justify-end
        user_selectors = [
            "div.self-end .break-words",
            ".user .break-words",
            "[data-role='user-message']",
            # final fallback:
            ".break-words"
        ]
        def _user_ok(d):
            txt = self._latest_nonempty_text(d, user_selectors)
            if not txt:
                return False
            if expected_substring is None:
                return txt
            return txt if expected_substring in txt else False

        return self.wait.until(_user_ok)

    def wait_for_reply(self):
        # Ensure our message actually posted before waiting for a reply
        self.wait_for_user_bubble()

        assistant_selectors = [
            "div.self-start .break-words",      # left/assistant alignment
            ".assistant .break-words",          # semantic hook if present
            "[data-role='assistant-message']",
            # broad fallback (kept last):
            ".break-words"
        ]

        def _assistant_ok(d):
            return self._latest_nonempty_text(d, assistant_selectors)

        try:
            return self.wait.until(_assistant_ok)
        except TimeoutException:
            # Debug aids: capture state to help diagnose future failures
            try:
                with open("/tmp/page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.driver.save_screenshot("/tmp/screen.png")
            except Exception:
                pass
            raise

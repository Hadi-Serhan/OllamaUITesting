# tests/main_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys  # <-- add this
import time
from .config import WAIT_TIMEOUT, MODEL_NAME

class MainPage:
    def __init__(self, driver, wait=None):
        self.driver = driver
        self.wait = wait or WebDriverWait(driver, WAIT_TIMEOUT,
                                          ignored_exceptions=(StaleElementReferenceException,))

    def open(self, url):
        self.driver.get(url)
        self.wait.until(lambda d: (d.title or "") != "")
        return self

    def _input_el(self):
        # Try common chat inputs in order
        for sel in ('textarea[name="message"]',
                    'input[name="message"]',
                    '[contenteditable="true"]',
                    'div[role="textbox"]'):
            els = self.driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                return els[0]
        return None

    def enter_message(self, message):
        el = self._input_el()
        if not el:
            raise RuntimeError("Chat input not found")
        if el.get_attribute("contenteditable") == "true":
            el.click()
            el.send_keys(message)
        else:
            el.clear()
            el.send_keys(message)
        return self

    def is_send_enabled(self):
        btns = self.driver.find_elements(By.CSS_SELECTOR, 'form button[type="submit"]')
        if not btns:
            return False
        return btns[0].is_enabled()

    def trigger_submit(self):
        """Click submit if enabled; otherwise press Enter in the input to trigger validation."""
        if self.is_send_enabled():
            self.driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').click()
        else:
            el = self._input_el()
            if not el:
                raise RuntimeError("Cannot trigger submit: input not found")
            el.send_keys(Keys.ENTER)  # common pattern for chat submit (also triggers validation)
        return self

    def wait_for_validation_message(self):
        """Wait for the validation bubble like 'Please provide an image for object detection.'"""
        KNOWN_SNIPPETS = [
            "Please provide an image for object detection",
            "attach an image",
            "image is required",
        ]
        def _val(d):
            nodes = d.find_elements(By.CSS_SELECTOR, '.break-words, [data-role="message-text"], .prose p')
            texts = [n.text.strip() for n in nodes if n.text.strip()]
            for t in reversed(texts):
                for s in KNOWN_SNIPPETS:
                    if s.lower() in t.lower():
                        return t
            return False
        return self.wait.until(_val)

    # (Optional) keep your existing helpers if you still use them elsewhere

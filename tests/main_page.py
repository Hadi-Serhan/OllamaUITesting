# tests/main_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from .config import WAIT_TIMEOUT

class MainPage:
    def __init__(self, driver, wait=None):
        self.driver = driver
        self.wait = wait or WebDriverWait(
            driver, WAIT_TIMEOUT,
            ignored_exceptions=(StaleElementReferenceException,)
        )

    def open(self, url):
        self.driver.get(url)
        self.wait.until(lambda d: (d.title or "") != "")
        return self

    # ---------- input helpers ----------
    def _input_el(self):
        for sel in (
            'textarea[name="message"]',
            'input[name="message"]',
            '[contenteditable="true"]',
            'div[role="textbox"]',
        ):
            els = self.driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                return els[0]
        return None

    def enter_message(self, message: str):
        el = self._input_el()
        if not el:
            raise RuntimeError("Chat input not found")
        el.click()
        if el.get_attribute("contenteditable") == "true":
            el.send_keys(message)
        else:
            try:
                el.clear()
            except Exception:
                pass
            el.send_keys(message)
        return self

    # ---------- submit + waits ----------
    def trigger_submit(self):
        """
        Always trigger the form submit via JS so it works even when the
        visible submit button is disabled.
        """
        el = self._input_el()
        if not el:
            raise RuntimeError("Cannot trigger submit: input not found")
        form = None
        try:
            form = el.find_element(By.XPATH, "ancestor::form")
        except Exception:
            form = None

        if form:
            self.driver.execute_script(
                """
                const f = arguments[0];
                if (f && typeof f.requestSubmit === 'function') f.requestSubmit();
                else if (f) f.submit();
                """,
                form
            )
        else:
            # Fallback: press Enter in the input
            el.send_keys(Keys.ENTER)
        return self

    def _all_message_texts(self):
        nodes = self.driver.find_elements(
            By.CSS_SELECTOR, ".break-words, [data-role='message-text'], .prose p"
        )
        return [n.text.strip() for n in nodes if (n.text or "").strip()]

    def wait_for_validation_message(self):
        """
        Accept any message that indicates an image is required, whether or not
        the transcript length changes after submit.
        """
        start_count = len(self._all_message_texts())
        KEYWORDS = ("image", "attach", "upload", "picture", "photo")

        def _val(d):
            texts = self._all_message_texts()
            # Prefer the newest message if we got a new bubble
            if len(texts) > start_count:
                last = texts[-1]
                if any(k in last.lower() for k in KEYWORDS):
                    return last
            # Otherwise scan backwards for any matching validation text
            for t in reversed(texts):
                if any(k in t.lower() for k in KEYWORDS):
                    return t
            return False

        return self.wait.until(_val)
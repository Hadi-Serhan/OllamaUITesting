import os, tempfile, shutil, unittest, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:3000')
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
BROWSER = os.getenv('BROWSER', 'chrome').lower()
W = int(os.getenv('SCREEN_WIDTH', '1920'))
H = int(os.getenv('SCREEN_HEIGHT', '1080'))

def make_chrome():
    opts = ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={W},{H}")
    # unique profile per runner to avoid "user data dir in use" in CI
    tmp_profile = tempfile.mkdtemp(prefix="chrome-profile-")
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument("--remote-debugging-port=0")
    driver = webdriver.Chrome(options=opts)
    driver._tmp_profile = tmp_profile
    return driver

def make_firefox():
    opts = FirefoxOptions()
    if HEADLESS:
        opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    driver.set_window_size(W, H)
    return driver

def first_present(driver, selectors, timeout=20):
    wait = WebDriverWait(driver, timeout)
    for sel in selectors:
        try:
            return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
        except Exception:
            continue
    raise TimeoutError(f"None of selectors became present: {selectors}")

class ExampleTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = make_chrome() if BROWSER == 'chrome' else make_firefox()
        self.wait = WebDriverWait(self.driver, 60)

    def tearDown(self):
        try:
            self.driver.quit()
        finally:
            tmp = getattr(self.driver, "_tmp_profile", None)
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)

    def test_page_title(self):
        self.driver.get(OLLAMA_URL)
        self.wait.until(lambda d: d.title is not None and len(d.title) > 0)
        self.assertRegex(self.driver.title, r"Ollama|LLM|Chat", "Unexpected page title")

    def test_send_message(self):
        self.driver.get(OLLAMA_URL)

        # Open model combobox (if present)
        try:
            combo = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='combobox']")))
            combo.click()
            # Pick the first option in the dialog/listbox
            option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[role='dialog'] [role='option], [role='listbox'] [role='option'], [role='menu'] [role='menuitem']")))
            option.click()
        except Exception:
            # If no combobox, assume a default model is already selected
            pass

        # Find the chat input (try several common patterns)
        chat_input = first_present(
            self.driver,
            [
                "form textarea",
                "textarea[placeholder*='message' i]",
                "form [contenteditable='true']",
                "form input[name='message']",
            ],
            timeout=30,
        )
        # Some UIs use contenteditable divs
        tag = chat_input.tag_name.lower()
        if tag == "textarea" or (tag == "input" and chat_input.get_attribute("type") in (None, "text")):
            chat_input.clear()
            chat_input.send_keys("Hi")
        else:
            self.driver.execute_script("arguments[0].innerText = 'Hi';", chat_input)

        send_btn = first_present(
            self.driver,
            [
                "form button[type='submit']",
                "form button:has(svg,path)",
                "form button",
            ],
            timeout=20,
        )
        self.wait.until(EC.element_to_be_clickable(send_btn)).click()

        # Wait for assistant reply (messages usually rendered with Tailwind's .break-words)
        self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".break-words")) >= 2)
        time.sleep(0.5)  # tiny buffer for stream completion
        msgs = self.driver.find_elements(By.CSS_SELECTOR, ".break-words")
        self.assertTrue(msgs[-1].text.strip() != "", "Model reply was empty")

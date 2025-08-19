
import os, tempfile, shutil, unittest, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from tests.main_page import MainPage

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:3000')
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
BROWSER  = os.getenv('BROWSER', 'chrome').lower()
W = int(os.getenv('SCREEN_WIDTH', '1920'))
H = int(os.getenv('SCREEN_HEIGHT', '1080'))

def make_chrome():
    opts = ChromeOptions()
    if HEADLESS:
        # use the modern headless (Chrome 109+)
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={W},{H}")
    # unique profile per run to avoid "user data dir in use"
    tmp_profile = tempfile.mkdtemp(prefix="chrome-profile-")
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument("--remote-debugging-port=0")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=opts
    )
    driver._tmp_profile = tmp_profile
    return driver

def make_firefox():
    opts = FirefoxOptions()
    if HEADLESS:
        opts.add_argument("--headless")
    # Use webdriver-manager to fetch geckodriver
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=opts
    )
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
        page = MainPage(self.driver, self.wait)
        page.open(OLLAMA_URL)
        self.assertRegex(self.driver.title, r"Ollama|LLM|Chat", "Unexpected page title")

    def test_send_message(self):
        page = MainPage(self.driver, self.wait)
        reply = (
            page.open(OLLAMA_URL)
                .select_model()
                .enter_message("Hi")
                .send_message()
                .wait_for_reply()
        )
        self.assertTrue(reply.strip() != "", "Model reply was empty")
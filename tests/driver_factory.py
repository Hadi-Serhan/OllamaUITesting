import tempfile, shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from .config import (
    BROWSER, HEADLESS, SCREEN_WIDTH as W, SCREEN_HEIGHT as H,
    CHROME_BIN, FIREFOX_BIN
)

class DriverFactory:
    def __init__(self, browser=BROWSER, width=W, height=H, headless=HEADLESS):
        self.browser = browser
        self.width = width
        self.height = height
        self.headless = headless

    def create(self):
        if self.browser == "chrome":
            return self._chrome()
        if self.browser == "firefox":
            return self._firefox()
        raise ValueError(f"Unsupported browser: {self.browser}")

    def _chrome(self):
        opts = ChromeOptions()
        if CHROME_BIN:
            opts.binary_location = CHROME_BIN
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(f"--window-size={self.width},{self.height}")
        opts.add_argument("--remote-debugging-port=0")
        # unique user-data-dir to avoid "in use" in CI
        tmp_profile = tempfile.mkdtemp(prefix="chrome-profile-")
        opts.add_argument(f"--user-data-dir={tmp_profile}")
        
        driver = webdriver.Chrome(options=opts)
        driver._tmp_profile = tmp_profile
        return driver

    def _firefox(self):
        opts = FirefoxOptions()
        if FIREFOX_BIN:
            opts.binary_location = FIREFOX_BIN
        if self.headless:
            opts.add_argument("--headless")

        driver = webdriver.Firefox(options=opts)
        driver.set_window_size(self.width, self.height)
        return driver


def build_driver():
    return DriverFactory().create()


def cleanup_driver(driver):
    try:
        driver.quit()
    finally:
        tmp = getattr(driver, "_tmp_profile", None)
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

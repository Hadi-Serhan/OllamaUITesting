import unittest
from selenium.webdriver.support.ui import WebDriverWait
from tests.config import OLLAMA_URL, WAIT_TIMEOUT
from tests.driver_factory import build_driver, cleanup_driver
from tests.main_page import MainPage

class ExampleTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = build_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        cleanup_driver(self.driver)

    def test_page_title(self):
        MainPage(self.driver, self.wait).open(OLLAMA_URL)
        self.assertRegex(self.driver.title, r"Ollama|LLM|Chat", "Unexpected page title")

    def test_send_message(self):
        reply = (
            MainPage(self.driver, self.wait)
            .open(OLLAMA_URL)
            .select_model()      # respects MODEL_NAME from config if set
            .enter_message("Hi")
            .send_message()
            .wait_for_reply()
        )
        self.assertTrue(reply.strip() != "", "Model reply was empty")

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

    # def test_send_message(self):
    #     reply = (
    #         MainPage(self.driver, self.wait)
    #         .open(OLLAMA_URL)
    #         .enter_message("Hi")
    #         .send_message()
    #         .wait_for_reply()
    #     )
    #     self.assertTrue(reply.strip() != "", "Model reply was empty")


    def test_validation_without_image(self):
        """When no image is attached, the UI should show a validation bubble."""
        page = MainPage(self.driver, self.wait).open(OLLAMA_URL).enter_message("Hi")
        page.trigger_submit()  # Click if enabled; otherwise send Enter to trigger validation
        msg = page.wait_for_validation_message()
        self.assertRegex(
            msg,
            r"Please provide an image for object detection|attach an image|image is required",
            "Expected a validation message when sending without an image",
        )
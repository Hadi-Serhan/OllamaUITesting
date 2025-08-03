import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:3000')


class ExampleTestCase(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 300)  # 60s wait to be safe

    def tearDown(self):
        self.driver.quit()

    def test_page_title(self):
        self.driver.get(OLLAMA_URL)
        self.assertIn('Ollama', self.driver.title)

    def test_send_message(self):
        self.driver.get(OLLAMA_URL)
        
        # Locate dropdown and choose a model
        model_dropdown = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='combobox']"))
        )
        model_dropdown.click()
        
        model_option = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='dialog'] button"))
        )
        model_option.click()
        
        # Locate the chat input by name and type a message
        chat_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "message"))
        )
        chat_input.clear()
        chat_input.send_keys("Hi")
        
        # Locate and click the send button (submit)
        send_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit']"))
        )
        send_button.click()

        # Wait for atleat 2 msgs
        self.wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".break-words")) >= 2 and
            d.find_elements(By.CSS_SELECTOR, ".break-words")[1].text.strip() != ""
        )
        
        # Extract model msg
        all_msgs = self.driver.find_elements(By.CSS_SELECTOR, ".break-words")
        latest_model_reply = all_msgs[-1]
        
        self.assertTrue(len(latest_model_reply.text.strip()) > 0)

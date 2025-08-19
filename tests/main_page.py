from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time

class MainPage:
    def __init__(self, driver, wait=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, 60, ignored_exceptions=(StaleElementReferenceException,))

    def open(self, url):
        self.driver.get(url)
        self.wait.until(lambda d: (d.title or "") != "")
        return self

    def select_model(self):
        # Locate dropdown and choose a model
        model_dropdown = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='combobox']"))
        )
        model_dropdown.click()
        
        model_option = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='dialog'] button"))
        )
        model_option.click()
        return self
        

    def enter_message(self, message):
        # Locate the chat input by name and type a message
        chat_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "message"))
        )
        chat_input.clear()
        chat_input.send_keys(message)
        return self
    
    def send_message(self):
        # Locate and click the send button (submit)
        send_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form button[type='submit']"))
        )
        send_button.click()
        return self
    
    
    def wait_for_reply(self):
        # Wait for atleat 2 msgs
        self.wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".break-words")) >= 2 and
            d.find_elements(By.CSS_SELECTOR, ".break-words")[1].text.strip() != ""
        )
        # Extract model msg
        all_msgs = self.driver.find_elements(By.CSS_SELECTOR, ".break-words")
        latest_model_reply = all_msgs[-1]
        return latest_model_reply.text.strip() if latest_model_reply else ""
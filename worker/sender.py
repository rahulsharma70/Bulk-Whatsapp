import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import logger
import config


class MessageSender:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    # =====================================================
    # PUBLIC
    # =====================================================
    def send_message(self, phone_number, message_text=None, attachment_path=None):
        try:
            phone = phone_number.replace("+", "").replace(" ", "")
            url = config.WHATSAPP_SEND_URL_TEMPLATE.format(phone)

            logger.info(f"Opening chat URL for {phone_number}")
            self.driver.get(url)
            time.sleep(1)

            if attachment_path:
                return self._send_attachment(attachment_path, message_text)

            if message_text:
                box = self._wait_footer_box()
                box.send_keys(message_text)
                box.send_keys(Keys.ENTER)
                return True, "Text sent"

            return False, "Nothing to send"

        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False, str(e)

    # =====================================================
    # ATTACHMENT (FINAL FIX)
    # =====================================================
    def _send_attachment(self, path, caption=None):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return False, "File not found"

        logger.info(f"Sending attachment: {path}")

        # Attach
        attach = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Attach']"))
        )
        self.driver.execute_script("arguments[0].click();", attach)
        time.sleep(0.3)

        menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[normalize-space()='Photos & videos']")
            )
        )
        self.driver.execute_script("arguments[0].click();", menu)

        file_input = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//input[@type='file']"))
        )[-1]
        file_input.send_keys(path)

        # 🔥 WAIT FOR PREVIEW (MANDATORY)
        logger.info("Waiting for image preview")
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src,'blob:')]"))
        )

        # 🔥 ADD CAPTION TO ACTIVE PREVIEW INPUT
        if caption:
            logger.info("Adding caption")
            time.sleep(0.2)
            active = self.driver.switch_to.active_element
            active.send_keys(Keys.CONTROL + "a", Keys.DELETE)
            active.send_keys(caption)

        # 🔥 SEND USING ACTIVE ELEMENT (NOT FOOTER)
        logger.info("Sending using ENTER on active element")
        time.sleep(0.2)
        self.driver.switch_to.active_element.send_keys(Keys.ENTER)

        logger.info("Attachment sent")
        return True, "Attachment sent"

    # =====================================================
    def _wait_footer_box(self):
        return self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//footer//div[@contenteditable='true']")
            )
        )

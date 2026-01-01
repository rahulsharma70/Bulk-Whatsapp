"""
WhatsApp Web session manager
Handles login, session health checks, and reconnection logic
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import logger
import config

class SessionManager:
    """
    Manages WhatsApp Web session lifecycle
    Handles login detection, session health, and reconnection
    """
    
    def __init__(self):
        """
        Initialize session manager
        """
        self.driver = None
        self.is_logged_in = False
        self._init_chrome_options()
    
    def _init_chrome_options(self):
        """
        Initialize Chrome options for WhatsApp Web
        """
        self.chrome_options = Options()
        
        # Use persistent profile (relative path like original)
        chrome_profile_dir = "./chrome_profile"
        os.makedirs(chrome_profile_dir, exist_ok=True)
        self.chrome_options.add_argument(f"--user-data-dir={chrome_profile_dir}")
        
        # Chrome options for stability (matching original working config)
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Experimental options
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
    
    def start_session(self):
        """
        Start Chrome browser and navigate to WhatsApp Web
        
        Returns:
            True if session started successfully
        """
        try:
            logger.info("Starting Chrome browser...")
            # Use Selenium Manager (built-in with Selenium 4.6+) - automatically handles driver setup
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Small delay to let Chrome fully initialize
            time.sleep(2)
            
            # Maximize window (works better than --start-maximized on macOS)
            try:
                self.driver.maximize_window()
            except Exception as e:
                logger.debug(f"Could not maximize window: {str(e)}")
                # Fallback if maximize doesn't work
                try:
                    self.driver.set_window_size(1920, 1080)
                except:
                    pass
            
            logger.info("Navigating to WhatsApp Web...")
            self.driver.get(config.WHATSAPP_BASE_URL)
            
            # Small delay after navigation to let page load
            time.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def check_login_status(self, timeout=None):
        """
        Check if user is logged in to WhatsApp Web
        
        Args:
            timeout: Maximum seconds to wait (default from config)
        
        Returns:
            True if logged in, False otherwise
        """
        if not self.driver:
            return False
        
        timeout = timeout or config.SESSION_TIMEOUT
        wait = WebDriverWait(self.driver, timeout)
        
        try:
            # Look for indicators that user is logged in
            # Search box, chat list, or side panel indicates login
            search_box = wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search')]")),
                    EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
                )
            )
            
            if search_box:
                logger.info("Login detected - user is logged in")
                self.is_logged_in = True
                return True
        except Exception as e:
            logger.debug(f"Login check: {str(e)}")
        
        self.is_logged_in = False
        return False
    
    def wait_for_login(self, timeout=None):
        """
        Wait for user to scan QR code and log in
        
        Args:
            timeout: Maximum seconds to wait (default from config)
        
        Returns:
            True if login successful, False if timeout
        """
        logger.info("Waiting for QR code scan...")
        timeout = timeout or config.SESSION_TIMEOUT
        
        # Check if already logged in
        if self.check_login_status(timeout=5):
            return True
        
        # Wait for login with longer timeout
        return self.check_login_status(timeout=timeout)
    
    def is_session_alive(self):
        """
        Check if browser session is still alive and responsive
        
        Returns:
            True if session is alive, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            # Try to get current URL
            _ = self.driver.current_url
            return True
        except Exception:
            logger.warning("Session is dead (browser closed or crashed)")
            return False
    
    def verify_logged_in(self):
        """
        Verify that user is still logged in (health check)
        
        Returns:
            True if still logged in, False if logged out or session dead
        """
        if not self.is_session_alive():
            self.is_logged_in = False
            return False
        
        try:
            # Quick check: look for search box or chat list
            wait = WebDriverWait(self.driver, config.LOGIN_CHECK_TIMEOUT)
            search_box = wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")),
                    EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
                )
            )
            
            if search_box:
                self.is_logged_in = True
                return True
        except Exception:
            pass
        
        # Check for QR code (logged out)
        try:
            qr_elements = self.driver.find_elements(By.XPATH, "//div[@data-ref] | //canvas")
            if qr_elements:
                logger.warning("QR code detected - user logged out")
                self.is_logged_in = False
                return False
        except:
            pass
        
        self.is_logged_in = False
        return False
    
    def get_driver(self):
        """
        Get the current Selenium driver instance
        
        Returns:
            WebDriver instance, or None if not started
        """
        return self.driver
    
    def close_session(self):
        """
        Close the browser session
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser session closed")
            except Exception as e:
                logger.error(f"Error closing session: {str(e)}")
            finally:
                self.driver = None
                self.is_logged_in = False
    
    def restart_session(self):
        """
        Restart the browser session (close and reopen)
        
        Returns:
            True if restart successful
        """
        logger.info("Restarting browser session...")
        self.close_session()
        time.sleep(2)  # Brief pause before restart
        return self.start_session()

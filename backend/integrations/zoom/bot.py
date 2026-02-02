"""
Simplified Zoom Bot for joining meetings and recording audio.
Adapted from cuemeet-zoom-bot for integration with Meeting Transcript backend.
"""

import os
import sys
import time
import uuid
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from .bot_utils import extract_zoom_details, manage_cookies

logger = logging.getLogger(__name__)


class ZoomBot:
    """Simplified Zoom bot for meeting integration."""
    
    def __init__(
        self,
        meeting_link: str,
        bot_name: str = "Meeting Transcript Bot",
        min_record_time: int = 7200,
        output_dir: str = "recordings"
    ):
        """
        Initialize Zoom bot.
        
        Args:
            meeting_link: Zoom meeting URL or ID
            bot_name: Display name in meeting
            min_record_time: Minimum recording time in seconds
            output_dir: Directory to save recordings
        """
        self.meeting_id, self.meeting_pwd = extract_zoom_details(meeting_link)
        self.bot_name = bot_name
        self.min_record_time = min_record_time
        self.browser = None
        self.id = str(uuid.uuid4())
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.recording_started = False
        
        logger.info(f"Zoom bot initialized: ID={self.id}, Meeting={self.meeting_id}")
    
    def setup_browser(self):
        """Setup headless Chrome browser with Selenium."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Media stream permissions
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 0,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 0
        })
        
        # User data directory
        user_data_dir = self.output_dir / f"browser_profile_{self.id}"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"user-data-dir={user_data_dir}")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=options)
            
            # Disable alerts
            self.browser.execute_script("""
                window.alert = function() { return; }
                window.confirm = function() { return true; }
                window.prompt = function() { return null; }
            """)
            
            logger.info("Browser launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            raise
    
    def navigate_to_meeting(self):
        """Navigate to Zoom meeting URL."""
        logger.info(f"Navigating to meeting ID: {self.meeting_id}")
        
        try:
            self.browser.get(f"https://zoom.us/wc/join/{self.meeting_id}")
            
            # Add cookies for auto-join
            for cookie in manage_cookies(self.bot_name):
                self.browser.add_cookie(cookie)
            
            self.browser.refresh()
            logger.info("Successfully navigated to meeting")
            time.sleep(2)
            
            # Check if meeting is invalid
            try:
                invalid_msg = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//span[contains(text(), 'This meeting link is invalid')]"
                    ))
                )
                if invalid_msg:
                    raise Exception("Meeting link is invalid")
            except TimeoutException:
                pass  # Meeting is valid
                
        except Exception as e:
            logger.error(f"Failed to navigate to meeting: {e}")
            raise
    
    def join_meeting(self):
        """Fill credentials and join meeting."""
        logger.info("Joining meeting...")
        
        try:
            # Enter password if required
            try:
                password_input = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='input-for-pwd']"))
                )
                if self.meeting_pwd:
                    password_input.send_keys(self.meeting_pwd)
                    logger.info("Entered meeting password")
            except TimeoutException:
                pass  # No password required
            
            # Enter bot name
            try:
                name_input = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@id='input-for-name']"))
                )
                name_input.clear()
                name_input.send_keys(self.bot_name)
                logger.info(f"Entered bot name: {self.bot_name}")
            except TimeoutException:
                pass
            
            time.sleep(2)
            
            # Click join button
            try:
                join_button = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Join")]'))
                )
                join_button.click()
                logger.info("Clicked join button")
            except TimeoutException:
                logger.warning("Join button not found - might have auto-joined")
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error joining meeting: {e}")
            raise
    
    def connect_audio(self):
        """Connect to audio and mute microphone."""
        logger.info("Connecting audio...")
        
        try:
            # Click "Join Audio" button
            try:
                audio_button = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Join Audio"]'))
                )
                audio_button.click()
                logger.info("Audio connected")
            except TimeoutException:
                logger.info("Audio already connected or button not found")
            
            time.sleep(1)
            
            # Mute audio
            try:
                mute_button = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//button[@aria-label="Mute" or @aria-label="Unmute"]'
                    ))
                )
                current_state = mute_button.get_attribute('aria-label')
                if current_state == "Mute":
                    mute_button.click()
                    logger.info("Audio muted")
                else:
                    logger.info("Audio already muted")
            except TimeoutException:
                pass
            
            # Stop video
            try:
                video_button = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//button[@aria-label="Stop Video" or @aria-label="Start Video"]'
                    ))
                )
                current_state = video_button.get_attribute('aria-label')
                if current_state == "Stop Video":
                    video_button.click()
                    logger.info("Video stopped")
                else:
                    logger.info("Video already stopped")
            except TimeoutException:
                pass
                
        except Exception as e:
            logger.error(f"Error connecting audio: {e}")
    
    def wait_for_admission(self, timeout=1800):
        """Wait for host to admit bot from waiting room."""
        logger.info("Checking for waiting room...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if in waiting room
                waiting_msg = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//span[contains(text(), 'host will admit you') or contains(text(), 'Waiting for the host')]"
                    ))
                )
                
                if waiting_msg:
                    logger.info("In waiting room, waiting for host to admit...")
                    time.sleep(10)
                    continue
                    
            except TimeoutException:
                # Not in waiting room or admitted
                break
        
        # Check if admitted
        try:
            participants = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Participants')]"))
            )
            if participants:
                logger.info("Admitted to meeting!")
                return True
        except TimeoutException:
            logger.warning("Could not confirm admission to meeting")
        
        return False
    
    def monitor_meeting(self):
        """Monitor meeting status and handle events."""
        logger.info(f"Monitoring meeting for up to {self.min_record_time} seconds...")
        
        start_time = time.time()
        
        while time.time() - start_time < self.min_record_time:
            try:
                # Check if meeting ended
                ended_msgs = [
                    "//div[contains(text(), 'meeting has been ended')]",
                    "//div[contains(text(), 'You have been removed')]",
                    "//span[contains(text(), 'call ended because everyone left')]"
                ]
                
                for xpath in ended_msgs:
                    try:
                        msg = WebDriverWait(self.browser, 2).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        if msg:
                            logger.info("Meeting ended - detected end message")
                            return
                    except TimeoutException:
                        continue
                
                # Check for unmute requests
                try:
                    unmute_request = self.browser.find_element(
                        By.XPATH,
                        "//div[contains(text(), 'would like you to unmute')]"
                    )
                    if unmute_request:
                        logger.info("Detected unmute request - staying muted")
                        # Click decline or close button if available
                except:
                    pass
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring meeting: {e}")
                break
        
        logger.info("Monitoring timeout reached")
    
    def cleanup(self):
        """Cleanup browser and resources."""
        logger.info("Cleaning up bot resources...")
        
        if self.browser:
            try:
                self.browser.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def run(self):
        """Main bot execution flow."""
        try:
            logger.info("Starting Zoom bot...")
            
            # Setup browser
            self.setup_browser()
            
            # Navigate and join
            self.navigate_to_meeting()
            self.join_meeting()
            self.connect_audio()
            
            # Wait for admission if in waiting room
            admitted = self.wait_for_admission()
            
            if not admitted:
                logger.warning("Could not confirm admission - continuing anyway")
            
            # Monitor meeting
            self.recording_started = True
            self.monitor_meeting()
            
            logger.info("Bot session completed successfully")
            
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise
        finally:
            self.cleanup()

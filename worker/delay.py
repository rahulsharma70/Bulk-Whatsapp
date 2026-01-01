"""
Human-like delay generator with randomization
Implements base delays and periodic long pauses
"""

import random
import time
from utils.logger import logger
import config

class DelayGenerator:
    """
    Generates randomized delays to simulate human behavior
    """
    
    def __init__(self, min_delay=None, max_delay=None):
        """
        Initialize delay generator
        
        Args:
            min_delay: Minimum delay in seconds (default from config)
            max_delay: Maximum delay in seconds (default from config)
        """
        self.min_delay = min_delay or config.MIN_DELAY
        self.max_delay = max_delay or config.MAX_DELAY
        self.message_count = 0
        self.long_pause_interval = config.LONG_PAUSE_INTERVAL
        self.long_pause_min = config.LONG_PAUSE_MIN
        self.long_pause_max = config.LONG_PAUSE_MAX
    
    def get_delay(self):
        """
        Get the next delay duration
        
        Returns:
            Delay duration in seconds (includes long pause if needed)
        """
        self.message_count += 1
        
        # Base delay (randomized)
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # Add long pause every N messages
        if self.message_count % self.long_pause_interval == 0:
            long_pause = random.uniform(self.long_pause_min, self.long_pause_max)
            logger.info(f"Long pause after {self.message_count} messages: {long_pause:.1f}s")
            delay += long_pause
        
        return delay
    
    def wait(self):
        """
        Wait for the calculated delay duration
        """
        delay = self.get_delay()
        logger.debug(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    def reset(self):
        """
        Reset message counter (useful for new jobs)
        """
        self.message_count = 0

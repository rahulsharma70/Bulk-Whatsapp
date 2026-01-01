#!/usr/bin/env python3
"""
Entry point to start the WhatsApp Bulk Sender Worker
Run this independently from Flask to process the message queue

Usage:
    python run_worker.py
    python run_worker.py --db-path custom_path.db
"""

from worker.worker import Worker
from utils.logger import logger
import sys

if __name__ == '__main__':
    logger.info("Starting WhatsApp Bulk Sender Worker...")
    logger.info("Press Ctrl+C to stop the worker")
    logger.info("-" * 60)
    
    worker = Worker()
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("\nWorker stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker crashed: {str(e)}", exc_info=True)
        sys.exit(1)

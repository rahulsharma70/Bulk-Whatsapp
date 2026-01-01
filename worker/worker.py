"""
Main worker process that processes the message queue
Long-running process that sends messages via WhatsApp Web
"""

import time
import signal
import sys
from datetime import datetime
from message_queue.queue_manager import QueueManager
from worker.session_manager import SessionManager
from worker.sender import MessageSender
from worker.delay import DelayGenerator
from utils.logger import logger
import config

class Worker:
    """
    Main worker class that processes messages from the queue
    Handles session management, sending, and job control
    """
    
    def __init__(self, db_path=None):
        """
        Initialize worker
        
        Args:
            db_path: Path to SQLite database (default: from config)
        """
        self.queue_manager = QueueManager(db_path)
        self.session_manager = SessionManager()
        self.sender = None
        self.delay_generator = None
        self.running = False
        self.current_job_id = None
        self.shutdown_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully
        """
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True
        self.running = False
    
    def start(self):
        """
        Start the worker process (main loop)
        """
        logger.info("=" * 60)
        logger.info("WhatsApp Bulk Sender Worker - Starting")
        logger.info("=" * 60)
        
        self.running = True
        
        # Start browser session
        if not self.session_manager.start_session():
            logger.error("Failed to start browser session")
            return
        
        # Wait for login
        logger.info("Waiting for WhatsApp Web login...")
        if not self.session_manager.wait_for_login():
            logger.error("Login timeout - please scan QR code and restart worker")
            self.session_manager.close_session()
            return
        
        logger.info("Login successful! Starting message processing...")
        
        # Initialize sender
        driver = self.session_manager.get_driver()
        if not driver:
            logger.error("Driver not available")
            return
        
        self.sender = MessageSender(driver)
        
        # Main processing loop
        try:
            self._process_loop()
        except Exception as e:
            logger.error(f"Fatal error in worker: {str(e)}", exc_info=True)
        finally:
            self._cleanup()
    
    def _process_loop(self):
        """
        Main processing loop - continuously processes messages from queue
        """
        last_session_check = time.time()
        
        while self.running and not self.shutdown_requested:
            try:
                # Check session health periodically
                current_time = time.time()
                if current_time - last_session_check > config.SESSION_CHECK_INTERVAL:
                    if not self.session_manager.verify_logged_in():
                        logger.warning("Session lost - pausing worker")
                        self._handle_session_loss()
                        last_session_check = current_time
                        time.sleep(5)  # Wait before retry
                        continue
                    last_session_check = current_time
                
                # Get next pending message
                message = self.queue_manager.dequeue_next_message()
                
                if not message:
                    # No pending messages - check for active jobs
                    active_jobs = self.queue_manager.get_active_jobs()
                    if not active_jobs:
                        # No active jobs - idle
                        time.sleep(config.WORKER_IDLE_DELAY)
                    else:
                        # Jobs exist but no pending messages - wait
                        time.sleep(config.WORKER_POLL_INTERVAL)
                    continue
                
                # Process message
                self._process_message(message)
                
                # Small delay between processing
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in processing loop: {str(e)}", exc_info=True)
                time.sleep(config.WORKER_POLL_INTERVAL)
    
    def _process_message(self, message):
        """
        Process a single message from the queue
        
        Args:
            message: Message dictionary from queue
        """
        message_id = message['message_id']
        job_id = message['job_id']
        phone_number = message['phone_number']
        message_text = message['message_text']
        attachment_path = message['attachment_path']
        
        # Update current job if changed
        if self.current_job_id != job_id:
            self.current_job_id = job_id
            job = self.queue_manager.get_job_status(job_id)
            if job:
                # Initialize delay generator for this job
                self.delay_generator = DelayGenerator(
                    min_delay=job['delay_min'],
                    max_delay=job['delay_max']
                )
                # Start job if pending
                if job['status'] == config.JOB_STATUS_PENDING:
                    self.queue_manager.start_job(job_id)
        
        # Check job status
        job = self.queue_manager.get_job_status(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found, skipping message {message_id}")
            return
        
        # Handle different job statuses
        if job['status'] == config.JOB_STATUS_STOPPED:
            logger.info(f"Job {job_id} is stopped, skipping message {message_id}")
            return
        elif job['status'] == config.JOB_STATUS_PAUSED:
            logger.debug(f"Job {job_id} is paused, waiting...")
            time.sleep(config.WORKER_POLL_INTERVAL)
            return
        elif job['status'] == config.JOB_STATUS_WAITING_FOR_LOGIN:
            logger.debug(f"Job {job_id} waiting for login, checking...")
            if self.session_manager.verify_logged_in():
                self.queue_manager.update_job_status(job_id, config.JOB_STATUS_RUNNING)
            else:
                time.sleep(config.WORKER_POLL_INTERVAL)
                return
        
        # Send message
        logger.info(f"Sending message {message_id} to {phone_number} (job {job_id})")
        
        success, error_message = self.sender.send_message(
            phone_number=phone_number,
            message_text=message_text,
            attachment_path=attachment_path
        )
        
        if success:
            # Mark as sent
            self.queue_manager.mark_sent(message_id)
            logger.info(f"Message {message_id} sent successfully")
            
            # Check if job is complete
            self._check_job_completion(job_id)
        else:
            # Mark as failed (with retry logic)
            retry_count = self.queue_manager.mark_failed(message_id, error_message)
            logger.warning(f"Message {message_id} failed: {error_message} (retry {retry_count}/{config.MAX_RETRY_ATTEMPTS})")
        
        # Apply delay after sending
        if self.delay_generator:
            self.delay_generator.wait()
    
    def _check_job_completion(self, job_id):
        """
        Check if a job is complete (all messages sent or failed)
        
        Args:
            job_id: ID of the job
        """
        job = self.queue_manager.get_job_status(job_id)
        if not job:
            return
        
        # Check if all messages are processed
        total = job['total_messages']
        sent = job['sent_count']
        failed = job['failed_count']
        
        if sent + failed >= total:
            # All messages processed
            self.queue_manager.update_job_status(
                job_id, 
                config.JOB_STATUS_COMPLETED,
                completed_at=datetime.now()
            )
            logger.info(f"Job {job_id} completed: {sent} sent, {failed} failed")
    
    def _handle_session_loss(self):
        """
        Handle session loss (logout, crash, etc.)
        Pauses active jobs and waits for reconnection
        """
        logger.warning("Session lost - pausing all active jobs")
        
        active_jobs = self.queue_manager.get_active_jobs()
        for job in active_jobs:
            if job['status'] == config.JOB_STATUS_RUNNING:
                self.queue_manager.update_job_status(
                    job['job_id'], 
                    config.JOB_STATUS_WAITING_FOR_LOGIN
                )
        
        # Try to restart session
        logger.info("Attempting to reconnect...")
        if self.session_manager.restart_session():
            if self.session_manager.wait_for_login(timeout=30):
                logger.info("Reconnected successfully - resuming jobs")
                # Resume jobs
                for job in active_jobs:
                    if job['status'] == config.JOB_STATUS_WAITING_FOR_LOGIN:
                        self.queue_manager.update_job_status(
                            job['job_id'], 
                            config.JOB_STATUS_RUNNING
                        )
            else:
                logger.error("Failed to reconnect - please scan QR code and restart worker")
        else:
            logger.error("Failed to restart session")
    
    def _cleanup(self):
        """
        Cleanup resources before shutdown
        """
        logger.info("Cleaning up worker resources...")
        
        # Close browser session (but keep it open if detach is set)
        # Session manager will handle this
        if self.session_manager:
            # Don't close if detach is enabled (user might want to keep browser open)
            # self.session_manager.close_session()
            pass
        
        logger.info("Worker shutdown complete")


def main():
    """
    Entry point for worker process
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Bulk Sender Worker')
    parser.add_argument('--db-path', type=str, help='Path to SQLite database', default=None)
    args = parser.parse_args()
    
    worker = Worker(db_path=args.db_path)
    
    try:
        worker.start()
    except Exception as e:
        logger.error(f"Worker crashed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

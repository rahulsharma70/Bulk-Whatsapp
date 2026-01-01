"""
Queue Manager - Interface for enqueueing and managing messages
Wraps JobStore with queue-specific operations
"""

from message_queue.job_store import JobStore
from utils.logger import logger
import config

class QueueManager:
    """
    High-level interface for managing the message queue
    Provides enqueue, dequeue, and job control operations
    """
    
    def __init__(self, db_path=None):
        """
        Initialize QueueManager
        
        Args:
            db_path: Path to SQLite database (default: from config)
        """
        self.job_store = JobStore(db_path)
    
    def enqueue_job(self, phone_numbers, message_text=None, attachment_path=None, 
                   delay_min=None, delay_max=None):
        """
        Create a new job and enqueue all messages
        
        Args:
            phone_numbers: List of phone numbers to send to
            message_text: Message text
            attachment_path: Path to attachment file (optional)
            delay_min: Minimum delay between messages
            delay_max: Maximum delay between messages
        
        Returns:
            job_id: ID of the created job
        """
        # Remove duplicates while preserving order
        unique_numbers = list(dict.fromkeys(phone_numbers))
        
        if not unique_numbers:
            raise ValueError("No phone numbers provided")
        
        # Validate message or attachment exists
        if not message_text and not attachment_path:
            raise ValueError("Either message_text or attachment_path must be provided")
        
        # Create job
        job_id = self.job_store.create_job(
            message_text=message_text,
            attachment_path=attachment_path,
            delay_min=delay_min or config.MIN_DELAY,
            delay_max=delay_max or config.MAX_DELAY
        )
        
        # Add messages to queue
        self.job_store.add_messages_to_job(
            job_id=job_id,
            phone_numbers=unique_numbers,
            message_text=message_text,
            attachment_path=attachment_path
        )
        
        logger.info(f"Job {job_id} enqueued with {len(unique_numbers)} messages")
        return job_id
    
    def dequeue_next_message(self, job_id=None):
        """
        Get the next pending message from the queue (FIFO)
        
        Args:
            job_id: Optional job ID to filter by
        
        Returns:
            Message dict, or None if no pending messages
        """
        return self.job_store.get_next_pending_message(job_id)
    
    def mark_sent(self, message_id):
        """
        Mark a message as successfully sent
        
        Args:
            message_id: ID of the message
        """
        self.job_store.mark_message_sent(message_id)
    
    def mark_failed(self, message_id, error_message=None):
        """
        Mark a message as failed (with retry logic)
        
        Args:
            message_id: ID of the message
            error_message: Error description
        
        Returns:
            retry_count: Number of retries attempted
        """
        return self.job_store.mark_message_failed(message_id, error_message, increment_retry=True)
    
    def start_job(self, job_id):
        """
        Mark a job as running (called by worker when starting)
        
        Args:
            job_id: ID of the job
        """
        from datetime import datetime
        self.job_store.update_job_status(
            job_id, 
            config.JOB_STATUS_RUNNING,
            started_at=datetime.now()
        )
    
    def pause_job(self, job_id):
        """
        Pause a running job
        
        Args:
            job_id: ID of the job
        """
        self.job_store.pause_job(job_id)
        logger.info(f"Job {job_id} paused")
    
    def resume_job(self, job_id):
        """
        Resume a paused job
        
        Args:
            job_id: ID of the job
        """
        self.job_store.resume_job(job_id)
        logger.info(f"Job {job_id} resumed")
    
    def stop_job(self, job_id):
        """
        Stop a job permanently
        
        Args:
            job_id: ID of the job
        """
        self.job_store.stop_job(job_id)
        logger.info(f"Job {job_id} stopped")
    
    def get_job_status(self, job_id):
        """
        Get job status and statistics
        
        Args:
            job_id: ID of the job
        
        Returns:
            Job information dict
        """
        return self.job_store.get_job_status(job_id)
    
    def get_job_messages(self, job_id, status=None):
        """
        Get all messages for a job
        
        Args:
            job_id: ID of the job
            status: Optional status filter
        
        Returns:
            List of message dictionaries
        """
        return self.job_store.get_job_messages(job_id, status)
    
    def get_active_jobs(self):
        """
        Get all active jobs
        
        Returns:
            List of job dictionaries
        """
        return self.job_store.get_active_jobs()
    
    def update_job_status(self, job_id, status, started_at=None, completed_at=None):
        """
        Update job status (used by worker)
        
        Args:
            job_id: ID of the job
            status: New status
            started_at: Optional start timestamp
            completed_at: Optional completion timestamp
        """
        self.job_store.update_job_status(job_id, status, started_at, completed_at)

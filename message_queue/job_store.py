"""
SQLite-based persistent storage for jobs and messages
Handles all database operations for campaign state
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from utils.logger import logger
import config

class JobStore:
    """
    Manages persistent storage of jobs and messages using SQLite
    """
    
    def __init__(self, db_path=None):
        """
        Initialize JobStore with database path
        
        Args:
            db_path: Path to SQLite database (default: from config)
        """
        self.db_path = db_path or config.DB_PATH
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections
        Ensures proper cleanup and transaction handling
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """
        Initialize database tables if they don't exist
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Jobs table - stores campaign/job information
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {config.JOBS_TABLE} (
                    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    message_text TEXT,
                    attachment_path TEXT,
                    delay_min INTEGER DEFAULT 4,
                    delay_max INTEGER DEFAULT 8,
                    total_messages INTEGER DEFAULT 0,
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Message queue table - stores individual messages
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {config.QUEUE_TABLE} (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    phone_number TEXT NOT NULL,
                    message_text TEXT,
                    attachment_path TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    last_attempt_at TIMESTAMP,
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES {config.JOBS_TABLE}(job_id) ON DELETE CASCADE
                )
            ''')
            
            # Index for faster queue operations
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_queue_status_job 
                ON {config.QUEUE_TABLE}(status, job_id)
            ''')
            
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_queue_pending 
                ON {config.QUEUE_TABLE}(status, message_id)
            ''')
            
            logger.info(f"Database initialized at {self.db_path}")
    
    def create_job(self, message_text=None, attachment_path=None, delay_min=None, delay_max=None):
        """
        Create a new job/campaign
        
        Args:
            message_text: Message text for the campaign
            attachment_path: Path to attachment file (optional)
            delay_min: Minimum delay between messages (default from config)
            delay_max: Maximum delay between messages (default from config)
        
        Returns:
            job_id: ID of the created job
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {config.JOBS_TABLE} 
                (status, message_text, attachment_path, delay_min, delay_max)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                config.JOB_STATUS_PENDING,
                message_text,
                attachment_path,
                delay_min or config.MIN_DELAY,
                delay_max or config.MAX_DELAY
            ))
            job_id = cursor.lastrowid
            logger.info(f"Created job {job_id}")
            return job_id
    
    def add_messages_to_job(self, job_id, phone_numbers, message_text=None, attachment_path=None):
        """
        Add multiple messages to a job
        
        Args:
            job_id: ID of the job
            phone_numbers: List of phone numbers
            message_text: Message text (overrides job default if provided)
            attachment_path: Attachment path (overrides job default if provided)
        
        Returns:
            Number of messages added
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get job defaults if not provided
            if message_text is None or attachment_path is None:
                cursor.execute(f'''
                    SELECT message_text, attachment_path 
                    FROM {config.JOBS_TABLE} 
                    WHERE job_id = ?
                ''', (job_id,))
                row = cursor.fetchone()
                if row:
                    job_message_text = row['message_text']
                    job_attachment_path = row['attachment_path']
                    message_text = message_text or job_message_text
                    attachment_path = attachment_path or job_attachment_path
            
            # Insert messages
            messages = []
            for phone in phone_numbers:
                messages.append((
                    job_id, phone, message_text, attachment_path,
                    config.MESSAGE_STATUS_PENDING
                ))
            
            cursor.executemany(f'''
                INSERT INTO {config.QUEUE_TABLE} 
                (job_id, phone_number, message_text, attachment_path, status)
                VALUES (?, ?, ?, ?, ?)
            ''', messages)
            
            # Update job total
            cursor.execute(f'''
                UPDATE {config.JOBS_TABLE}
                SET total_messages = (
                    SELECT COUNT(*) FROM {config.QUEUE_TABLE} WHERE job_id = ?
                ),
                updated_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
            ''', (job_id, job_id))
            
            count = len(messages)
            logger.info(f"Added {count} messages to job {job_id}")
            return count
    
    def get_next_pending_message(self, job_id=None):
        """
        Get the next pending message from the queue (FIFO)
        
        Args:
            job_id: Optional job ID to filter by
        
        Returns:
            Message row as dict, or None if no pending messages
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if job_id:
                cursor.execute(f'''
                    SELECT * FROM {config.QUEUE_TABLE}
                    WHERE status = ? AND job_id = ?
                    ORDER BY message_id ASC
                    LIMIT 1
                ''', (config.MESSAGE_STATUS_PENDING, job_id))
            else:
                cursor.execute(f'''
                    SELECT * FROM {config.QUEUE_TABLE}
                    WHERE status = ?
                    ORDER BY message_id ASC
                    LIMIT 1
                ''', (config.MESSAGE_STATUS_PENDING,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def mark_message_sent(self, message_id):
        """
        Mark a message as successfully sent
        
        Args:
            message_id: ID of the message
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE {config.QUEUE_TABLE}
                SET status = ?, sent_at = CURRENT_TIMESTAMP,
                    last_attempt_at = CURRENT_TIMESTAMP
                WHERE message_id = ?
            ''', (config.MESSAGE_STATUS_SENT, message_id))
            
            # Update job statistics
            cursor.execute(f'''
                SELECT job_id FROM {config.QUEUE_TABLE} WHERE message_id = ?
            ''', (message_id,))
            row = cursor.fetchone()
            if row:
                job_id = row['job_id']
                self._update_job_stats(job_id, conn)
    
    def mark_message_failed(self, message_id, error_message=None, increment_retry=True):
        """
        Mark a message as failed and increment retry count
        
        Args:
            message_id: ID of the message
            error_message: Error message describing the failure
            increment_retry: Whether to increment retry count (default: True)
        
        Returns:
            retry_count: Current retry count after increment
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current retry count
            cursor.execute(f'''
                SELECT retry_count, job_id FROM {config.QUEUE_TABLE} 
                WHERE message_id = ?
            ''', (message_id,))
            row = cursor.fetchone()
            
            if not row:
                return 0
            
            retry_count = row['retry_count']
            job_id = row['job_id']
            
            if increment_retry:
                retry_count += 1
            
            # Determine new status
            if retry_count < config.MAX_RETRY_ATTEMPTS:
                new_status = config.MESSAGE_STATUS_PENDING  # Retry
            else:
                new_status = config.MESSAGE_STATUS_FAILED  # Permanent failure
            
            cursor.execute(f'''
                UPDATE {config.QUEUE_TABLE}
                SET status = ?, retry_count = ?, 
                    last_attempt_at = CURRENT_TIMESTAMP,
                    error_message = ?
                WHERE message_id = ?
            ''', (new_status, retry_count, error_message, message_id))
            
            # Update job statistics
            self._update_job_stats(job_id, conn)
            
            return retry_count
    
    def _update_job_stats(self, job_id, conn):
        """
        Update job statistics (sent_count, failed_count)
        
        Args:
            job_id: ID of the job
            conn: Database connection (must be from context manager)
        """
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE {config.JOBS_TABLE}
            SET sent_count = (
                SELECT COUNT(*) FROM {config.QUEUE_TABLE} 
                WHERE job_id = ? AND status = ?
            ),
            failed_count = (
                SELECT COUNT(*) FROM {config.QUEUE_TABLE} 
                WHERE job_id = ? AND status = ?
            ),
            updated_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        ''', (job_id, config.MESSAGE_STATUS_SENT, 
              job_id, config.MESSAGE_STATUS_FAILED, 
              job_id))
    
    def update_job_status(self, job_id, status, started_at=None, completed_at=None):
        """
        Update job status
        
        Args:
            job_id: ID of the job
            status: New status
            started_at: Optional start timestamp
            completed_at: Optional completion timestamp
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            update_fields = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
            params = [status, job_id]
            
            if started_at:
                update_fields.append('started_at = ?')
                params.insert(-1, started_at)
            
            if completed_at:
                update_fields.append('completed_at = ?')
                params.insert(-1, completed_at)
            
            cursor.execute(f'''
                UPDATE {config.JOBS_TABLE}
                SET {', '.join(update_fields)}
                WHERE job_id = ?
            ''', params)
            
            logger.info(f"Job {job_id} status updated to {status}")
    
    def get_job_status(self, job_id):
        """
        Get job status and statistics
        
        Args:
            job_id: ID of the job
        
        Returns:
            Job information as dict, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {config.JOBS_TABLE} WHERE job_id = ?
            ''', (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_job_messages(self, job_id, status=None):
        """
        Get all messages for a job, optionally filtered by status
        
        Args:
            job_id: ID of the job
            status: Optional status filter
        
        Returns:
            List of message dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(f'''
                    SELECT * FROM {config.QUEUE_TABLE}
                    WHERE job_id = ? AND status = ?
                    ORDER BY message_id ASC
                ''', (job_id, status))
            else:
                cursor.execute(f'''
                    SELECT * FROM {config.QUEUE_TABLE}
                    WHERE job_id = ?
                    ORDER BY message_id ASC
                ''', (job_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def pause_job(self, job_id):
        """
        Pause a job by updating its status
        
        Args:
            job_id: ID of the job
        """
        self.update_job_status(job_id, config.JOB_STATUS_PAUSED)
    
    def resume_job(self, job_id):
        """
        Resume a paused job
        
        Args:
            job_id: ID of the job
        """
        job = self.get_job_status(job_id)
        if job and job['status'] == config.JOB_STATUS_PAUSED:
            self.update_job_status(job_id, config.JOB_STATUS_RUNNING)
    
    def stop_job(self, job_id):
        """
        Stop a job (marks as stopped, worker will stop processing)
        
        Args:
            job_id: ID of the job
        """
        self.update_job_status(job_id, config.JOB_STATUS_STOPPED)
    
    def get_active_jobs(self):
        """
        Get all active jobs (running or paused)
        
        Returns:
            List of job dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {config.JOBS_TABLE}
                WHERE status IN (?, ?, ?)
                ORDER BY job_id DESC
            ''', (config.JOB_STATUS_RUNNING, 
                  config.JOB_STATUS_PAUSED,
                  config.JOB_STATUS_WAITING_FOR_LOGIN))
            return [dict(row) for row in cursor.fetchall()]

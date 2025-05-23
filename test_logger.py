import unittest
import os
import shutil
from pathlib import Path
from datetime import datetime
import re
from unittest.mock import patch

# Add project root to sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from logger import log_activity
from project import create_project # To set up a realistic project context

class TestLogger(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = Path("temp_test_logger_base")
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        self.test_base_dir.mkdir(parents=True, exist_ok=True)

        self.project_name = "LoggingTestProject"
        # create_project will also make an initial log entry.
        create_project(self.project_name, base_path=str(self.test_base_dir))
        self.project_path = self.test_base_dir / self.project_name
        self.log_file_path = self.project_path / "activity_log.txt"

    def tearDown(self):
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)

    def test_log_activity_appends_messages(self):
        # The first message is from create_project
        initial_message_count = 0
        if self.log_file_path.exists():
            with open(self.log_file_path, 'r') as f:
                initial_message_count = len(f.readlines())
        
        messages_to_log = [
            "User logged in.",
            "Data processing started.",
            "Task completed successfully."
        ]

        for msg in messages_to_log:
            log_activity(str(self.project_path), msg)

        self.assertTrue(self.log_file_path.exists())
        with open(self.log_file_path, 'r') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), initial_message_count + len(messages_to_log))

        for i, logged_msg in enumerate(messages_to_log):
            # Check message content (accounting for the initial log from create_project)
            self.assertIn(logged_msg, lines[initial_message_count + i])
            # Check timestamp format
            self.assertRegex(lines[initial_message_count + i], r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] ")

    def test_log_activity_creates_file_if_not_exists(self):
        # Delete the log file that might have been created by setUp's create_project
        if self.log_file_path.exists():
            self.log_file_path.unlink()
        
        self.assertFalse(self.log_file_path.exists()) # Ensure it's gone

        message = "System initialized after log file deletion."
        log_activity(str(self.project_path), message)

        self.assertTrue(self.log_file_path.exists())
        with open(self.log_file_path, 'r') as f:
            content = f.read()
        
        self.assertIn(message, content)
        self.assertRegex(content, r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] " + re.escape(message))

    def test_log_activity_with_non_existent_project_path(self):
        non_existent_path = self.test_base_dir / "ThisPathDoesNotExist"
        message = "This should not be logged."

        # We expect log_activity to print an error but not raise one.
        # And no log file should be created at this bogus path.
        log_activity(str(non_existent_path), message)
        
        self.assertFalse((non_existent_path / "activity_log.txt").exists())
        # Further checks could involve capturing stderr if framework supports easily.

    @patch('logger.datetime') # Patch datetime object within logger.py
    def test_log_activity_with_mocked_timestamp(self, mock_datetime):
        # Configure the mock datetime.now() to return a fixed time
        fixed_timestamp = datetime(2023, 10, 26, 14, 30, 15)
        mock_datetime.now.return_value = fixed_timestamp

        # Delete existing log to ensure clean state for this specific test
        if self.log_file_path.exists():
            self.log_file_path.unlink()

        message = "Mocked timestamp test."
        log_activity(str(self.project_path), message)

        expected_log_entry = f"[{fixed_timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
        
        self.assertTrue(self.log_file_path.exists())
        with open(self.log_file_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, expected_log_entry)

if __name__ == '__main__':
    unittest.main()

import unittest
import os
import shutil
from pathlib import Path
import json
from datetime import datetime
import re

# Add project root to sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from node import (
    _sanitize_title, 
    create_node, 
    get_node_path, 
    save_chat_message, 
    save_notes, 
    save_summary, 
    get_previous_node_summary
)
from project import create_project # To set up a project context

class TestNode(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = Path("temp_test_node_base")
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        self.test_base_dir.mkdir(parents=True, exist_ok=True)

        self.project_name = "NodeTestProject"
        create_project(self.project_name, base_path=str(self.test_base_dir))
        self.project_path = self.test_base_dir / self.project_name

    def tearDown(self):
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)

    def test_sanitize_title(self):
        self.assertEqual(_sanitize_title("My Test Title!"), "my_test_title")
        self.assertEqual(_sanitize_title("  Leading & Trailing Spaces  "), "leading_trailing_spaces")
        self.assertEqual(_sanitize_title("Special_Chars*($)"), "special_chars")
        self.assertEqual(_sanitize_title("already-lowercase-and-valid"), "already-lowercase-and-valid")
        self.assertEqual(_sanitize_title(""), "") # Empty string remains empty

    def test_create_node_successful(self):
        node_title = "First Node - Basics"
        sanitized = _sanitize_title(node_title)
        node_dir_path = self.project_path / "nodes" / sanitized
        
        returned_path = create_node(str(self.project_path), node_title)
        self.assertEqual(returned_path, node_dir_path)

        self.assertTrue(node_dir_path.exists())
        self.assertTrue(node_dir_path.is_dir())
        self.assertTrue((node_dir_path / "chat_history.jsonl").exists())
        self.assertTrue((node_dir_path / "notes.md").exists())
        self.assertTrue((node_dir_path / "summary.txt").exists())

    def test_create_node_empty_or_invalid_title(self):
        with self.assertRaises(ValueError) as context:
            create_node(str(self.project_path), "!!!") # Sanitizes to empty
        self.assertIn("Sanitized node title cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            create_node(str(self.project_path), "  ") # Sanitizes to empty
        self.assertIn("Sanitized node title cannot be empty", str(context.exception))

    def test_create_node_already_exists(self):
        node_title = "Existing Node"
        create_node(str(self.project_path), node_title) # Create first time
        with self.assertRaises(FileExistsError):
            create_node(str(self.project_path), node_title) # Try creating again

    def test_get_node_path_constructs_correctly(self):
        node_title = "My Path Test Node"
        sanitized = _sanitize_title(node_title)
        expected_path = self.project_path / "nodes" / sanitized
        self.assertEqual(get_node_path(str(self.project_path), node_title), expected_path)

    def test_save_chat_message_appends_and_formats(self):
        node_title = "Chatty Node"
        create_node(str(self.project_path), node_title)
        chat_file = get_node_path(str(self.project_path), node_title) / "chat_history.jsonl"

        messages = [
            ("user", "Hello AI!"),
            ("ai", "Hello User! How can I help?"),
            ("user", "Tell me about Python.")
        ]

        for sender, msg_text in messages:
            save_chat_message(str(self.project_path), node_title, sender, msg_text)

        with open(chat_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), len(messages))
        for i, line_str in enumerate(lines):
            entry = json.loads(line_str)
            self.assertIn("timestamp", entry)
            self.assertRegex(entry["timestamp"], r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
            self.assertEqual(entry["sender"], messages[i][0])
            self.assertEqual(entry["message"], messages[i][1])

    def test_save_chat_message_to_non_existent_node(self):
        with self.assertRaises(FileNotFoundError):
            save_chat_message(str(self.project_path), "Ghost Node", "user", "test")

    def test_save_notes_writes_and_overwrites_content(self):
        node_title = "Notes Node"
        create_node(str(self.project_path), node_title)
        notes_file = get_node_path(str(self.project_path), node_title) / "notes.md"

        content1 = "Initial notes about topic X."
        save_notes(str(self.project_path), node_title, content1)
        with open(notes_file, 'r') as f:
            self.assertEqual(f.read(), content1)

        content2 = "Updated notes, topic X is complex."
        save_notes(str(self.project_path), node_title, content2)
        with open(notes_file, 'r') as f:
            self.assertEqual(f.read(), content2)
            
    def test_save_notes_to_non_existent_node(self):
        with self.assertRaises(FileNotFoundError):
            save_notes(str(self.project_path), "Ghost Node Notes", "some notes")

    def test_save_summary_writes_and_overwrites_content(self):
        node_title = "Summary Node"
        create_node(str(self.project_path), node_title)
        summary_file = get_node_path(str(self.project_path), node_title) / "summary.txt"

        content1 = "Initial summary."
        save_summary(str(self.project_path), node_title, content1)
        with open(summary_file, 'r') as f:
            self.assertEqual(f.read(), content1)

        content2 = "Revised summary, more concise."
        save_summary(str(self.project_path), node_title, content2)
        with open(summary_file, 'r') as f:
            self.assertEqual(f.read(), content2)

    def test_save_summary_to_non_existent_node(self):
        with self.assertRaises(FileNotFoundError):
            save_summary(str(self.project_path), "Ghost Node Summary", "some summary")

    def test_get_previous_node_summary_first_node(self):
        # Assumes all_nodes_ordered_list contains sanitized titles as per node.py implementation
        self.assertIsNone(get_previous_node_summary(str(self.project_path), 0, ["node_a", "node_b"]))

    def test_get_previous_node_summary_returns_correct_summary(self):
        node_a_title = "Node A - Previous"
        node_b_title = "Node B - Current"
        
        create_node(str(self.project_path), node_a_title)
        create_node(str(self.project_path), node_b_title)
        
        summary_a_content = "This is the summary for Node A."
        save_summary(str(self.project_path), node_a_title, summary_a_content)
        
        # node.py's get_previous_node_summary expects sanitized titles in the list
        all_sanitized_nodes = [_sanitize_title(node_a_title), _sanitize_title(node_b_title)]
        
        retrieved_summary = get_previous_node_summary(str(self.project_path), 1, all_sanitized_nodes)
        self.assertEqual(retrieved_summary, summary_a_content)

    def test_get_previous_node_summary_missing_file(self):
        node_c_title = "Node C - Prev Missing Summary"
        node_d_title = "Node D - Current Needs Prev Summary"

        create_node(str(self.project_path), node_c_title) # Summary file is touched but empty
        create_node(str(self.project_path), node_d_title)
        
        # Ensure summary.txt for Node C is empty or non-existent for a stricter test
        # create_node touches summary.txt, so it exists. If it's empty, read() returns "".
        # The function expects "Summary not found for previous node." if file is missing,
        # but an empty file would return "". Let's test the "not found" case explicitly.
        node_c_summary_path = get_node_path(str(self.project_path), node_c_title) / "summary.txt"
        if node_c_summary_path.exists():
            node_c_summary_path.unlink() # Delete it

        all_sanitized_nodes = [_sanitize_title(node_c_title), _sanitize_title(node_d_title)]
        retrieved_summary = get_previous_node_summary(str(self.project_path), 1, all_sanitized_nodes)
        self.assertEqual(retrieved_summary, "Summary not found for previous node.")

    def test_get_previous_node_summary_index_out_of_bounds(self):
        all_sanitized_nodes = ["node_x", "node_y"]
        with self.assertRaises(IndexError):
            get_previous_node_summary(str(self.project_path), 2, all_sanitized_nodes) # Index 2 for list of len 2
        with self.assertRaises(IndexError): # Also check for too large index if list is small
            get_previous_node_summary(str(self.project_path), 10, all_sanitized_nodes)

    def test_get_previous_node_summary_empty_list(self):
        # If all_nodes_ordered_list is empty
        self.assertIsNone(get_previous_node_summary(str(self.project_path), 0, []))
        # An index error would occur if index > 0 and list is empty, but index 0 with empty list should be None
        # However, if index is 0, it short-circuits to return None.
        # If index is >0 and list is empty, it depends on how it's structured.
        # current_node_index > len(all_nodes_ordered_list) -1
        # 1 > 0 - 1 (i.e. 1 > -1) -> True, raises IndexError. This is correct.
        with self.assertRaises(IndexError):
             get_previous_node_summary(str(self.project_path), 1, [])


if __name__ == '__main__':
    unittest.main()

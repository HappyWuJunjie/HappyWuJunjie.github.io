import unittest
import os
import shutil
from pathlib import Path

# Add project root to sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from outline import add_outline_item, get_outline_items
from project import create_project # To set up a project context

class TestOutline(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = Path("temp_test_outline_base")
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        self.test_base_dir.mkdir(parents=True, exist_ok=True)

        self.project_name = "OutlineTestProject"
        create_project(self.project_name, base_path=str(self.test_base_dir))
        self.project_path = self.test_base_dir / self.project_name
        self.outline_file_path = self.project_path / "outline.md"

        # Ensure outline.md is empty before each test method for predictable results
        if self.outline_file_path.exists():
            with open(self.outline_file_path, 'w') as f: # Truncate file
                f.write("") 

    def tearDown(self):
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)

    def test_add_main_heading(self):
        add_outline_item(str(self.project_path), "Main Topic 1", is_main_heading=True)
        with open(self.outline_file_path, 'r') as f:
            content = f.read()
        self.assertIn("# Main Topic 1\n", content)

    def test_add_sub_item(self):
        add_outline_item(str(self.project_path), "Sub Point A", is_main_heading=False)
        with open(self.outline_file_path, 'r') as f:
            content = f.read()
        self.assertIn("  - Sub Point A\n", content)

    def test_add_multiple_items(self):
        add_outline_item(str(self.project_path), "Chapter 1", True)
        add_outline_item(str(self.project_path), "Section 1.1", False)
        add_outline_item(str(self.project_path), "Chapter 2", True)
        
        with open(self.outline_file_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(lines[0], "# Chapter 1\n")
        self.assertEqual(lines[1], "  - Section 1.1\n")
        self.assertEqual(lines[2], "# Chapter 2\n")

    def test_get_outline_items_empty(self):
        # outline.md is already empty due to setUp
        items = get_outline_items(str(self.project_path))
        self.assertEqual(items, [])

    def test_get_outline_items_returns_only_main_headings(self):
        add_outline_item(str(self.project_path), "Main 1", True)
        add_outline_item(str(self.project_path), "Sub 1.1", False)
        add_outline_item(str(self.project_path), "Main 2 with trailing space   ", True)
        add_outline_item(str(self.project_path), "  Sub 2.1 with leading space", False)
        add_outline_item(str(self.project_path), "  # Not a real heading", False) # Sub-item that looks like a heading

        items = get_outline_items(str(self.project_path))
        self.assertEqual(items, ["Main 1", "Main 2 with trailing space"])

    def test_get_outline_items_stripping(self):
        add_outline_item(str(self.project_path), "  My Heading  ", True)
        items = get_outline_items(str(self.project_path))
        self.assertEqual(items, ["My Heading"])
        
        # Test with "# " prefix already in item_text (should be handled by strip)
        # Current add_outline_item prepends "# " so this would become "## My Heading"
        # Let's assume item_text is the raw text for the heading.
        # The function `get_outline_items` should strip "# " from lines starting with it.
        with open(self.outline_file_path, 'w') as f: # overwrite
            f.write("# # Double Hash Heading\n") # Manually write a malformed line
            f.write("# Single Hash Heading\n")
        items = get_outline_items(str(self.project_path))
        # It should take the line as is and strip the first "# "
        self.assertEqual(items, ["# Double Hash Heading", "Single Hash Heading"])


    def test_add_item_to_non_existent_project(self):
        non_existent_project_path = str(self.test_base_dir / "GhostProject")
        with self.assertRaises(FileNotFoundError) as context:
            add_outline_item(non_existent_project_path, "Test")
        self.assertIn(f"Project directory '{non_existent_project_path}' not found", str(context.exception))


    def test_get_items_from_non_existent_project(self):
        non_existent_project_path = str(self.test_base_dir / "GhostProject")
        with self.assertRaises(FileNotFoundError) as context: # This error is from outline_file_path.exists() check
            get_outline_items(non_existent_project_path)
        self.assertIn(f"Outline file '{Path(non_existent_project_path) / 'outline.md'}' not found", str(context.exception))


    def test_add_item_if_outline_md_missing(self):
        self.assertTrue(self.outline_file_path.exists()) # Exists due to create_project
        self.outline_file_path.unlink() # Delete it
        self.assertFalse(self.outline_file_path.exists())

        with self.assertRaises(FileNotFoundError) as context:
            add_outline_item(str(self.project_path), "Test")
        self.assertIn(f"Outline file '{self.outline_file_path}' not found", str(context.exception))

    def test_get_items_if_outline_md_missing(self):
        self.assertTrue(self.outline_file_path.exists())
        self.outline_file_path.unlink()
        self.assertFalse(self.outline_file_path.exists())

        with self.assertRaises(FileNotFoundError) as context:
            get_outline_items(str(self.project_path))
        self.assertIn(f"Outline file '{self.outline_file_path}' not found", str(context.exception))

    def test_add_empty_or_whitespace_item_text(self):
        # outline.py's add_outline_item prints a warning and skips.
        # We verify that no new content is added.
        initial_content = ""
        if self.outline_file_path.exists():
             with open(self.outline_file_path, 'r') as f:
                initial_content = f.read()
        
        add_outline_item(str(self.project_path), "", is_main_heading=True)
        add_outline_item(str(self.project_path), "   ", is_main_heading=False)
        
        with open(self.outline_file_path, 'r') as f:
            final_content = f.read()
        
        self.assertEqual(initial_content, final_content, "Content should not change when adding empty/whitespace items.")
        
        # Ensure get_outline_items still returns empty if only empty items were "added"
        items = get_outline_items(str(self.project_path))
        self.assertEqual(items, [])


if __name__ == '__main__':
    unittest.main()

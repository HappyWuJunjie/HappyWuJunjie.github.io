import unittest
import os
import shutil
from pathlib import Path
import time # For unique project names if needed, or just careful cleanup

# Add project root to sys.path to allow direct import of modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))) # Assuming test files are in root with .py files

from project import create_project
# logger.log_activity is used by create_project, so its basic functionality is implicitly tested.

class TestProject(unittest.TestCase):

    def setUp(self):
        # Create a temporary base directory for testing
        self.test_base_dir = Path("temp_test_projects_base")
        # Ensure it's clean before a test, though tearDown should handle most cases
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        self.test_base_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Remove the temporary base directory and all its contents after tests
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)

    def test_create_project_successful(self):
        project_name = "TestProject1"
        project_path = self.test_base_dir / project_name

        create_project(project_name, base_path=str(self.test_base_dir))

        # Assert project directory exists
        self.assertTrue(project_path.exists())
        self.assertTrue(project_path.is_dir())

        # Assert standard files and directories exist
        self.assertTrue((project_path / "outline.md").exists())
        self.assertTrue((project_path / "prompts.json").exists())
        self.assertTrue((project_path / "activity_log.txt").exists())
        self.assertTrue((project_path / "nodes").exists())
        self.assertTrue((project_path / "nodes").is_dir())

        # Check log message in activity_log.txt
        with open(project_path / "activity_log.txt", 'r') as f:
            log_content = f.read()
        self.assertIn(f"Project created: {project_name}", log_content)
        # Check for timestamp format (basic check)
        self.assertRegex(log_content, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")


    def test_create_project_already_exists(self):
        project_name = "TestProjectExists"
        # Create the project once
        create_project(project_name, base_path=str(self.test_base_dir))

        # Try to create it again and expect FileExistsError
        with self.assertRaises(FileExistsError) as context:
            create_project(project_name, base_path=str(self.test_base_dir))
        self.assertIn(f"Project directory '{self.test_base_dir / project_name}' already exists.", str(context.exception))

    def test_create_project_creates_base_path_if_not_exists(self):
        project_name = "TestProjectInNewBase"
        new_base_path = self.test_base_dir / "new_level_base"
        # new_base_path should not exist at this point

        project_path = new_base_path / project_name

        create_project(project_name, base_path=str(new_base_path))

        # Assert the new base path was created
        self.assertTrue(new_base_path.exists())
        self.assertTrue(new_base_path.is_dir())

        # Assert project directory exists within the new base path
        self.assertTrue(project_path.exists())
        self.assertTrue(project_path.is_dir())

        # Assert standard files exist (spot check)
        self.assertTrue((project_path / "activity_log.txt").exists())
        with open(project_path / "activity_log.txt", 'r') as f:
            log_content = f.read()
        self.assertIn(f"Project created: {project_name}", log_content)

if __name__ == '__main__':
    unittest.main()

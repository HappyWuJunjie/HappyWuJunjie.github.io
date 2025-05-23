import os
from pathlib import Path
from datetime import datetime

# For the __main__ block, we'll need create_project
try:
    from project import create_project
except ImportError:
    print("Warning: project.py not found. create_project function will not be available for the demo in logger.py.")
    # Mock create_project if project.py is not available for the demo
    def create_project(project_name: str, base_path: str = '.'):
        print(f"Mock create_project called for {project_name} at {base_path}.")
        project_dir = Path(base_path) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        # Simulate activity_log.txt creation for the logger demo
        # In the actual refactored version, create_project would call log_activity,
        # which would create this file.
        (project_dir / "activity_log.txt").touch()
        (project_dir / "outline.md").touch()
        (project_dir / "nodes").mkdir(exist_ok=True)
        (project_dir / "prompts.json").touch()


def log_activity(project_path: str, message: str):
    """
    Appends a timestamped message to activity_log.txt in the given project_path.

    Args:
        project_path: The path to the project directory.
        message: The message to log.

    Handles IOError during file operations. If project_path itself does not exist,
    this function will not create it and an error will likely occur.
    """
    proj_path = Path(project_path)
    
    # It's assumed project_path exists as a directory.
    # If not, .is_dir() will be false, or open() later might fail if proj_path is a file.
    if not proj_path.is_dir():
        print(f"Error: Project path '{project_path}' does not exist or is not a directory. Cannot log activity.")
        return

    log_file_path = proj_path / "activity_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    try:
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except IOError as e:
        print(f"IOError: Could not write to log file '{log_file_path}'. Error: {e}")

if __name__ == '__main__':
    TEST_PROJECT_LOGGER = "TestProjectForLogger"
    # Clean up previous test run
    import shutil
    if Path(TEST_PROJECT_LOGGER).exists():
        print(f"Cleaning up existing '{TEST_PROJECT_LOGGER}' directory...")
        shutil.rmtree(TEST_PROJECT_LOGGER)
    
    print(f"Setting up '{TEST_PROJECT_LOGGER}' for logger demonstration...")
    # This call to create_project will, after refactoring project.py,
    # make the first log entry using the new log_activity function.
    try:
        # Ensure project.py is available and create_project can be called
        # If project.py (and its own logger import) isn't fully set up, this might need adjustment
        # For now, assume project.py will be refactored and this will work.
        create_project(TEST_PROJECT_LOGGER) 
        print(f"Project '{TEST_PROJECT_LOGGER}' created.\n")

        # Now, log more activities directly using logger.py's function
        print(f"Logging additional activities to '{TEST_PROJECT_LOGGER}'...")
        log_activity(TEST_PROJECT_LOGGER, "User performed action X.")
        log_activity(TEST_PROJECT_LOGGER, "System completed task Y.")
        log_activity(TEST_PROJECT_LOGGER, "Another important event Z occurred.")
        print("Additional activities logged.\n")

        # Verify the content of activity_log.txt
        log_file_to_check = Path(TEST_PROJECT_LOGGER) / "activity_log.txt"
        if log_file_to_check.exists():
            print(f"Contents of '{log_file_to_check}':")
            with open(log_file_to_check, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            print(f"Error: Log file '{log_file_to_check}' not found. This indicates an issue.")
            print("This might happen if create_project (or its mock) didn't create the log,")
            print("or if the refactoring of project.py to use logger.log_activity is not yet complete or has issues.")

        # Test logging to a non-existent project path
        print("\nTesting log_activity with a non-existent project path...")
        log_activity("NonExistentProject123", "This message should not be logged successfully.")
        # Expected: "Error: Project path 'NonExistentProject123' does not exist or is not a directory. Cannot log activity."
        
        print("\nLogger demonstration finished.")

    except ImportError:
         print("Critical Error: Could not import 'create_project' from 'project'.")
         print("This is needed for logger.py's __main__ demonstration.")
         print("Make sure project.py is in the same directory and syntactically correct.")
    except Exception as e:
        print(f"An unexpected error occurred during logger demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print(f"\nCleaning up '{TEST_PROJECT_LOGGER}' directory post-test...")
        if Path(TEST_PROJECT_LOGGER).exists():
            shutil.rmtree(TEST_PROJECT_LOGGER)
            print(f"'{TEST_PROJECT_LOGGER}' directory cleaned up.")
        else:
            print(f"'{TEST_PROJECT_LOGGER}' directory not found for cleanup.")

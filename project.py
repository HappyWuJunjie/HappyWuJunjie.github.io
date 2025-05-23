import os
# import datetime # Removed as logging is handled by logger.py
from pathlib import Path # Added for consistency, though os.path is used below. Will refactor if time permits.
from logger import log_activity # Import the new logging function

def create_project(project_name: str, base_path: str = '.'):
    """
    Creates a new project with a predefined structure.

    Args:
        project_name: The name of the project.
        base_path: The base directory where the project will be created. Defaults to current directory.

    Raises:
        FileExistsError: If the project directory already exists.
    """
    # Using os.path for now, can be changed to Path later for full consistency
    project_path_str = os.path.join(base_path, project_name) 
    project_path_obj = Path(project_path_str) # For using Path methods if needed

    # Create base_path if it doesn't exist
    if not os.path.exists(base_path): # os.path.exists works with string
        os.makedirs(base_path)
        print(f"Base path '{base_path}' created.")

    if os.path.exists(project_path_str):
        raise FileExistsError(f"Project directory '{project_path_str}' already exists.")

    # Create project structure
    os.makedirs(project_path_str)
    os.makedirs(os.path.join(project_path_str, 'nodes'))

    # Create empty files - activity_log.txt will be created by log_activity if it doesn't exist
    open(os.path.join(project_path_str, 'outline.md'), 'a').close()
    open(os.path.join(project_path_str, 'prompts.json'), 'a').close()
    # The line below that created activity_log.txt is removed as log_activity handles it.
    # open(os.path.join(project_path_str, 'activity_log.txt'), 'a').close() 

    # Log project creation using the centralized logger
    # Pass the string representation of the path if log_activity expects a string
    log_activity(project_path_str, f"Project created: {project_name}")

if __name__ == '__main__':
    # Need to ensure logger.py is available for this to run
    # For testing, we might need to adjust sys.path or ensure files are in the right place.
    # Assuming logger.py is in the same directory / PYTHONPATH.

    # Temp lists for cleanup
    projects_to_cleanup = []
    custom_paths_to_cleanup = []

    try:
        # First creation attempt
        project1_name = "MyNewLearningProject"
        create_project(project1_name)
        projects_to_cleanup.append(project1_name)
        print(f"Project '{project1_name}' created successfully in the current directory.")

        # Verify content of activity_log.txt for the first project
        project1_log_path = os.path.join(project1_name, "activity_log.txt")
        if os.path.exists(project1_log_path):
            with open(project1_log_path, 'r') as f:
                print(f"Contents of {project1_log_path}:")
                log_content = f.read()
                print(log_content)
                assert f"Project created: {project1_name}" in log_content, "Log message missing or incorrect."
        else:
            print(f"Error: {project1_log_path} not found after creation.")


        # Second creation attempt (should fail)
        print(f"\nAttempting to create project '{project1_name}' again (should fail)...")
        create_project(project1_name) # This line should not be reached
    except FileExistsError as e:
        print(f"Error as expected: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*30 + "\n")

    try:
        # Third creation attempt in a custom base_path
        project2_name = "MySecondProject"
        custom_path = "custom_projects"
        custom_paths_to_cleanup.append(custom_path)

        create_project(project2_name, base_path=custom_path)
        # project_path_in_custom = os.path.join(custom_path, project2_name) # Not directly used for cleanup list
        print(f"Project '{project2_name}' created successfully in '{custom_path}'.")

        # Verify content of activity_log.txt for the second project
        project2_log_path = os.path.join(custom_path, project2_name, "activity_log.txt")
        if os.path.exists(project2_log_path):
            with open(project2_log_path, 'r') as f:
                print(f"Contents of {project2_log_path}:")
                log_content = f.read()
                print(log_content)
                assert f"Project created: {project2_name}" in log_content, "Log message missing or incorrect."
        else:
            print(f"Error: {project2_log_path} not found after creation.")

        # Fourth creation attempt in custom base_path (should fail)
        print(f"\nAttempting to create project '{project2_name}' in '{custom_path}' again (should fail)...")
        create_project(project2_name, base_path=custom_path) # This line should not be reached
    except FileExistsError as e:
        print(f"Error as expected: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up created directories for idempotency
        import shutil
        for proj_name in projects_to_cleanup:
            if os.path.exists(proj_name):
                shutil.rmtree(proj_name)
                print(f"Cleaned up '{proj_name}'.")
        for cp_name in custom_paths_to_cleanup:
            if os.path.exists(cp_name):
                shutil.rmtree(cp_name)
                print(f"Cleaned up '{cp_name}'.")
        print("project.py __main__ finished.")

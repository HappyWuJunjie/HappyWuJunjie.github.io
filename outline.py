import os
from pathlib import Path

# Attempt to import create_project from project.py for the __main__ block.
# If project.py is not found, the __main__ block will fail, which is acceptable for this task
# as the functions themselves do not depend on it.
try:
    from project import create_project
except ImportError:
    # This is a fallback for environments where project.py might not be directly importable
    # or for testing outline.py in isolation without running its __main__ block.
    print("Warning: project.py not found. create_project function will not be available for the demo.")
    def create_project(project_name: str, base_path: str = '.'):
        print(f"Mock create_project called for {project_name} at {base_path}. In a real scenario, this would create a project.")
        # Simulate project creation for outline.py's __main__ block if project.py is missing
        project_dir = Path(base_path) / project_name
        project_dir.mkdir(parents=True, exist_ok=True) # Ensure base_path/project_name exists
        (project_dir / "outline.md").touch() # Ensure outline.md exists for the demo
        (project_dir / "nodes").mkdir(exist_ok=True)
        (project_dir / "prompts.json").touch()
        (project_dir / "activity_log.txt").touch()


def add_outline_item(project_path: str, item_text: str, is_main_heading: bool = True):
    """
    Appends an item to the outline.md file in the specified project.

    Args:
        project_path: The path to the project directory.
        item_text: The text of the outline item.
        is_main_heading: True if the item is a main heading, False for a sub-item.

    Raises:
        FileNotFoundError: If project_path or outline.md does not exist.
    """
    proj_path = Path(project_path)
    if not proj_path.exists() or not proj_path.is_dir():
        raise FileNotFoundError(f"Project directory '{project_path}' not found or is not a directory.")

    outline_file_path = proj_path / "outline.md"
    if not outline_file_path.exists():
        # This check is per instruction, though project.create_project should create it.
        raise FileNotFoundError(f"Outline file '{outline_file_path}' not found.")

    if not item_text.strip():
        # Avoid adding empty lines as headings or items
        print("Warning: Attempted to add empty item_text. Skipping.")
        return

    formatted_item = ""
    if is_main_heading:
        formatted_item = f"# {item_text.strip()}\n"
    else:
        formatted_item = f"  - {item_text.strip()}\n"

    with open(outline_file_path, 'a', encoding='utf-8') as f:
        f.write(formatted_item)

def get_outline_items(project_path: str) -> list[str]:
    """
    Retrieves a list of main headings from outline.md.

    Args:
        project_path: The path to the project directory.

    Returns:
        A list of strings, where each string is a main heading without the '# ' prefix.

    Raises:
        FileNotFoundError: If outline.md does not exist.
    """
    proj_path = Path(project_path)
    outline_file_path = proj_path / "outline.md"

    if not outline_file_path.exists():
        raise FileNotFoundError(f"Outline file '{outline_file_path}' not found.")

    headings = []
    with open(outline_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("# "):
                headings.append(stripped_line[2:].strip())
    return headings

if __name__ == '__main__':
    TEST_PROJECT_NAME_OUTLINE = "TestProjectForOutline"
    # Clean up previous test run if any
    import shutil
    if Path(TEST_PROJECT_NAME_OUTLINE).exists():
        print(f"Cleaning up existing '{TEST_PROJECT_NAME_OUTLINE}' directory...")
        shutil.rmtree(TEST_PROJECT_NAME_OUTLINE)

    try:
        print(f"Attempting to create project: {TEST_PROJECT_NAME_OUTLINE}")
        create_project(TEST_PROJECT_NAME_OUTLINE) # From project.py
        project_outline_path = Path(TEST_PROJECT_NAME_OUTLINE)
        print(f"Project '{TEST_PROJECT_NAME_OUTLINE}' created.\n")

        # 1. Get initial outline items (should be empty)
        print("Getting initial outline items...")
        initial_items = get_outline_items(str(project_outline_path))
        print(f"Initial main headings: {initial_items}")
        assert initial_items == [], f"Expected empty list for initial items, got {initial_items}"
        print("Initial check successful (no headings).\n")

        # 2. Add main headings
        print("Adding main headings...")
        add_outline_item(str(project_outline_path), "Introduction", is_main_heading=True)
        add_outline_item(str(project_outline_path), "Core Concepts", is_main_heading=True)
        add_outline_item(str(project_outline_path), "Advanced Topics", is_main_heading=True)
        print("Main headings added.\n")

        # 3. Get outline items after adding main headings
        print("Getting outline items after adding main headings...")
        main_headings = get_outline_items(str(project_outline_path))
        print(f"Main headings: {main_headings}")
        expected_main_headings = ["Introduction", "Core Concepts", "Advanced Topics"]
        assert main_headings == expected_main_headings, f"Expected {expected_main_headings}, got {main_headings}"
        print("Main headings retrieval successful.\n")

        # 4. Add sub-items
        print("Adding sub-items...")
        add_outline_item(str(project_outline_path), "What is X?", is_main_heading=False) # Sub for Introduction
        add_outline_item(str(project_outline_path), "Key Feature 1", is_main_heading=False) # Sub for Core Concepts
        add_outline_item(str(project_outline_path), "Key Feature 2", is_main_heading=False) # Sub for Core Concepts
        add_outline_item(str(project_outline_path), "Nuance A", is_main_heading=False) # Sub for Advanced Topics
        print("Sub-items added.\n")

        # 5. Verify content of outline.md (optional manual check step)
        outline_content_path = project_outline_path / "outline.md"
        print(f"Content of '{outline_content_path}':")
        with open(outline_content_path, 'r') as f:
            print(f.read())
        print("")

        # 6. Get outline items again (should still be only main headings)
        print("Getting outline items after adding sub-items (should only return main headings)...")
        main_headings_after_subs = get_outline_items(str(project_outline_path))
        print(f"Main headings: {main_headings_after_subs}")
        assert main_headings_after_subs == expected_main_headings, \
            f"Expected {expected_main_headings}, got {main_headings_after_subs}. Sub-items should not be included."
        print("Main headings retrieval after adding sub-items successful.\n")

        # 7. Test adding an empty item (should be skipped)
        print("Attempting to add an empty item...")
        add_outline_item(str(project_outline_path), "   ", is_main_heading=True) # Empty main heading
        add_outline_item(str(project_outline_path), "", is_main_heading=False) # Empty sub-item
        current_headings = get_outline_items(str(project_outline_path))
        assert current_headings == expected_main_headings, "Empty items should not be added."
        print("Empty items were not added, as expected.\n")

        # 8. Test with non-existent project path for add_outline_item
        print("Testing add_outline_item with non-existent project path...")
        try:
            add_outline_item("NonExistentProject", "Test Item")
        except FileNotFoundError as e:
            print(f"Caught expected error: {e}\n")

        # 9. Test with non-existent project path for get_outline_items
        print("Testing get_outline_items with non-existent project path...")
        try:
            get_outline_items("NonExistentProject")
        except FileNotFoundError as e:
            print(f"Caught expected error: {e}\n")

        # 10. Test with existing project but missing outline.md (simulate this by deleting it)
        print("Testing with existing project but missing outline.md...")
        if outline_content_path.exists():
            outline_content_path.unlink() # Delete outline.md
            print(f"Temporarily deleted {outline_content_path} for testing.")
        
        try:
            add_outline_item(str(project_outline_path), "Item after delete")
        except FileNotFoundError as e:
            print(f"Caught expected error for add_outline_item (outline.md missing): {e}")
        
        try:
            get_outline_items(str(project_outline_path))
        except FileNotFoundError as e:
            print(f"Caught expected error for get_outline_items (outline.md missing): {e}")
        
        print("\nAll demonstrations finished.")

    except FileExistsError as e:
        print(f"Demo error (FileExistsError): {e}")
    except FileNotFoundError as e:
        print(f"Demo error (FileNotFoundError): {e}")
    except AssertionError as e:
        print(f"Demo assertion error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Optional: Clean up the test project directory
        # print(f"\nCleaning up '{TEST_PROJECT_NAME_OUTLINE}' directory post-test...")
        # if Path(TEST_PROJECT_NAME_OUTLINE).exists():
        #     shutil.rmtree(TEST_PROJECT_NAME_OUTLINE)
        #     print(f"'{TEST_PROJECT_NAME_OUTLINE}' directory cleaned up.")
        pass

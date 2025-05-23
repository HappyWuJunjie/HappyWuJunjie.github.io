import os
import re
import json
from pathlib import Path
from datetime import datetime

# Assuming project.py is in the same directory and its functions can be imported.
# If project.py is not found, the __main__ block will fail, which is acceptable for this task.
try:
    from project import create_project
except ImportError:
    # This is a fallback for environments where project.py might not be directly importable
    # or for testing node.py in isolation without running its __main__ block.
    print("Warning: project.py not found. create_project function will not be available for the demo.")
    def create_project(project_name: str, base_path: str = '.'):
        print(f"Mock create_project called for {project_name} at {base_path}. In a real scenario, this would create a project.")
        # Simulate project creation for node.py's __main__ block if project.py is missing
        project_dir = Path(base_path) / project_name
        (project_dir / "nodes").mkdir(parents=True, exist_ok=True)
        (project_dir / "outline.md").touch()
        (project_dir / "prompts.json").touch()
        (project_dir / "activity_log.txt").touch()


def _sanitize_title(title: str) -> str:
    """
    Sanitizes a title to be filesystem-friendly.
    Allows alphanumeric characters, hyphens, and underscores.
    Replaces spaces with underscores and converts to lowercase.
    """
    title = title.lower()
    title = title.replace(' ', '_')
    # Invalid characters are removed first.
    title = re.sub(r'[^a-z0-9_-]', '', title)
    # Then, condense any multiple underscores that might have formed.
    title = re.sub(r'_+', '_', title)
    title = title.strip('_') # Finally, strip any leading/trailing underscores.
    return title

def create_node(project_path: str, node_title: str) -> Path:
    """
    Creates a new node subdirectory and its initial files.
    """
    sanitized_title = _sanitize_title(node_title)
    if not sanitized_title:
        raise ValueError("Sanitized node title cannot be empty. Please provide a valid title.")

    node_dir = Path(project_path) / 'nodes' / sanitized_title

    if node_dir.exists():
        raise FileExistsError(f"Node directory '{node_dir}' already exists.")

    node_dir.mkdir(parents=True)

    (node_dir / 'chat_history.jsonl').touch()
    (node_dir / 'notes.md').touch()
    (node_dir / 'summary.txt').touch()

    return node_dir

def get_node_path(project_path: str, node_title: str) -> Path:
    """
    Constructs and returns the path to the node directory. Does not check for existence.
    """
    sanitized_title = _sanitize_title(node_title)
    if not sanitized_title:
        # Consistent with create_node, though often get_node_path might be called with potentially non-existing titles
        # Depending on usage, one might argue this check is not strictly needed here if only used by other functions
        # that already validate or handle path non-existence.
        raise ValueError("Sanitized node title cannot be empty. Please provide a valid title for path construction.")
    return Path(project_path) / 'nodes' / sanitized_title

def save_chat_message(project_path: str, node_title: str, sender: str, message: str):
    """
    Appends a chat message to the node's chat_history.jsonl file.
    """
    node_dir = get_node_path(project_path, node_title)
    chat_file = node_dir / 'chat_history.jsonl'

    if not node_dir.exists():
        raise FileNotFoundError(f"Node directory '{node_dir}' does not exist.")
    if not chat_file.exists():
         # This case should ideally not happen if create_node was called, but good for robustness
        chat_file.touch() # Create if somehow missing

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "sender": sender, "message": message}

    with open(chat_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def save_notes(project_path: str, node_title: str, content: str):
    """
    Overwrites the notes.md file in the node directory.
    """
    node_dir = get_node_path(project_path, node_title)
    notes_file = node_dir / 'notes.md'

    if not node_dir.exists():
        raise FileNotFoundError(f"Node directory '{node_dir}' does not exist.")

    with open(notes_file, 'w') as f:
        f.write(content)

def save_summary(project_path: str, node_title: str, content: str):
    """
    Overwrites the summary.txt file in the node directory.
    """
    node_dir = get_node_path(project_path, node_title)
    summary_file = node_dir / 'summary.txt'

    if not node_dir.exists():
        raise FileNotFoundError(f"Node directory '{node_dir}' does not exist.")

    with open(summary_file, 'w') as f:
        f.write(content)

def get_previous_node_summary(project_path: str, current_node_index: int, all_nodes_ordered_list: list[str]) -> str | None:
    """
    Fetches the summary of the previous node in the ordered list.
    all_nodes_ordered_list contains sanitized node titles.
    """
    if current_node_index == 0:
        return None
    if current_node_index > len(all_nodes_ordered_list) -1 :
        raise IndexError("current_node_index is out of bounds for all_nodes_ordered_list.")
    if not all_nodes_ordered_list:
        return None # Or raise error if list shouldn't be empty

    previous_node_sanitized_title = all_nodes_ordered_list[current_node_index - 1]
    
    # We use get_node_path which expects an original title, but here we have a sanitized one.
    # This implies all_nodes_ordered_list should store original titles or _sanitize_title is idempotent
    # For now, assume all_nodes_ordered_list contains titles that _sanitize_title can correctly map.
    # A better approach might be to have get_node_path_sane(project_path, sanitized_node_title)
    # or ensure _sanitize_title is consistently used.
    # Let's assume the list contains titles that can be passed to get_node_path.
    # If all_nodes_ordered_list has *sanitized* titles, then get_node_path would re-sanitize.
    # This should be fine if sanitizing an already sanitized string doesn't change it.
    previous_node_dir = Path(project_path) / 'nodes' / previous_node_sanitized_title # Construct path directly
    summary_file = previous_node_dir / 'summary.txt'

    if not summary_file.exists():
        return "Summary not found for previous node." # As per requirement

    with open(summary_file, 'r') as f:
        return f.read()

if __name__ == '__main__':
    TEST_PROJECT_NAME = "TestProjectForNodes"
    # Clean up previous test run if any - BE CAREFUL WITH THIS IN REAL SCENARIOS
    # For a sandbox, this is fine.
    import shutil
    if Path(TEST_PROJECT_NAME).exists():
        print(f"Cleaning up existing '{TEST_PROJECT_NAME}' directory...")
        shutil.rmtree(TEST_PROJECT_NAME)

    try:
        print(f"Attempting to create project: {TEST_PROJECT_NAME}")
        create_project(TEST_PROJECT_NAME) # From project.py
        print(f"Project '{TEST_PROJECT_NAME}' created.\n")

        NODE_1_TITLE = "First Chapter - Introduction"
        NODE_2_TITLE = "Second Chapter - Deep Dive"

        # 1. Create Node 1
        print(f"Attempting to create node: '{NODE_1_TITLE}'")
        node1_path = create_node(TEST_PROJECT_NAME, NODE_1_TITLE)
        print(f"Node '{NODE_1_TITLE}' (sanitized: '{node1_path.name}') created at: {node1_path}\n")

        # 2. Get Node 1 path
        retrieved_node1_path = get_node_path(TEST_PROJECT_NAME, NODE_1_TITLE)
        print(f"Retrieved path for '{NODE_1_TITLE}': {retrieved_node1_path}")
        assert node1_path == retrieved_node1_path
        print("Path retrieval successful.\n")

        # 3. Save chat messages to Node 1
        print(f"Saving chat messages to '{NODE_1_TITLE}'...")
        save_chat_message(TEST_PROJECT_NAME, NODE_1_TITLE, "user", "Hello, this is my first thought.")
        save_chat_message(TEST_PROJECT_NAME, NODE_1_TITLE, "ai", "Hello user, I'm here to help.")
        print("Chat messages saved. Check:", retrieved_node1_path / 'chat_history.jsonl', "\n")

        # 4. Save notes to Node 1
        print(f"Saving notes to '{NODE_1_TITLE}'...")
        notes_content_node1 = "This is an introduction to the topic. It covers A, B, and C."
        save_notes(TEST_PROJECT_NAME, NODE_1_TITLE, notes_content_node1)
        print("Notes saved. Check:", retrieved_node1_path / 'notes.md', "\n")

        # 5. Save summary to Node 1
        print(f"Saving summary to '{NODE_1_TITLE}'...")
        summary_content_node1 = "Node 1 is about the basics."
        save_summary(TEST_PROJECT_NAME, NODE_1_TITLE, summary_content_node1)
        print("Summary saved. Check:", retrieved_node1_path / 'summary.txt', "\n")

        # 6. Attempt to create Node 1 again (should fail)
        print(f"Attempting to create node '{NODE_1_TITLE}' again (should fail)...")
        try:
            create_node(TEST_PROJECT_NAME, NODE_1_TITLE)
        except FileExistsError as e:
            print(f"Caught expected error: {e}\n")

        # 7. Create Node 2
        print(f"Attempting to create node: '{NODE_2_TITLE}'")
        node2_path = create_node(TEST_PROJECT_NAME, NODE_2_TITLE)
        print(f"Node '{NODE_2_TITLE}' (sanitized: '{node2_path.name}') created at: {node2_path}\n")
        
        # 8. Save summary to Node 2 (just to have a file there)
        summary_content_node2 = "Node 2 explores advanced concepts."
        save_summary(TEST_PROJECT_NAME, NODE_2_TITLE, summary_content_node2)
        print(f"Summary saved for '{NODE_2_TITLE}'.\n")


        # 9. Use get_previous_node_summary
        # Assume `all_nodes_ordered_list` comes from outline.md or similar logic
        # The titles in this list should be the *original* titles if get_node_path is to be used internally by get_previous_node_summary
        # Or, if they are sanitized, get_previous_node_summary needs to handle that.
        # The current implementation of get_previous_node_summary constructs path directly using sanitized title.
        
        all_sanitized_nodes = [_sanitize_title(NODE_1_TITLE), _sanitize_title(NODE_2_TITLE)]
        
        print(f"Testing get_previous_node_summary for '{NODE_1_TITLE}' (index 0):")
        prev_summary_for_node1 = get_previous_node_summary(TEST_PROJECT_NAME, 0, all_sanitized_nodes)
        print(f"Previous summary for Node 1: {prev_summary_for_node1}")
        assert prev_summary_for_node1 is None
        print("Correctly returned None for the first node.\n")

        print(f"Testing get_previous_node_summary for '{NODE_2_TITLE}' (index 1):")
        prev_summary_for_node2 = get_previous_node_summary(TEST_PROJECT_NAME, 1, all_sanitized_nodes)
        print(f"Previous summary for Node 2 (should be from Node 1): '{prev_summary_for_node2}'")
        assert prev_summary_for_node2 == summary_content_node1
        print("Correctly retrieved summary of Node 1.\n")

        # Test edge case for get_previous_node_summary: previous summary file doesn't exist
        print("Testing get_previous_node_summary when previous summary file is missing...")
        # Create a temporary Node 3 for this test
        NODE_3_TITLE = "Third Chapter - Epilogue"
        node3_path = create_node(TEST_PROJECT_NAME, NODE_3_TITLE)
        all_sanitized_nodes_temp = [_sanitize_title(NODE_1_TITLE), _sanitize_title(NODE_2_TITLE), _sanitize_title(NODE_3_TITLE)]
        
        # Ensure Node 2 (previous to Node 3) has no summary for this specific test
        # We can delete it, or save an empty string (current implementation returns "Summary not found...")
        # Let's delete summary of Node 2 to test "Summary not found..."
        (get_node_path(TEST_PROJECT_NAME, NODE_2_TITLE) / "summary.txt").unlink()

        summary_for_node3_from_node2 = get_previous_node_summary(TEST_PROJECT_NAME, 2, all_sanitized_nodes_temp)
        print(f"Previous summary for Node 3 (Node 2 summary deleted): '{summary_for_node3_from_node2}'")
        assert summary_for_node3_from_node2 == "Summary not found for previous node."
        print("Correctly handled missing previous summary file.\n")


        # Test FileNotFoundError for save operations if node does not exist
        print("Testing save operations for a non-existent node (should fail)...")
        NON_EXISTENT_NODE = "Non Existent Node"
        try:
            save_notes(TEST_PROJECT_NAME, NON_EXISTENT_NODE, "some notes")
        except FileNotFoundError as e:
            print(f"Caught expected error for save_notes: {e}")
        try:
            save_summary(TEST_PROJECT_NAME, NON_EXISTENT_NODE, "some summary")
        except FileNotFoundError as e:
            print(f"Caught expected error for save_summary: {e}")
        try:
            save_chat_message(TEST_PROJECT_NAME, NON_EXISTENT_NODE, "user", "test")
        except FileNotFoundError as e:
            print(f"Caught expected error for save_chat_message: {e}")

        print("\nAll demonstrations finished.")

    except FileExistsError as e:
        print(f"Demo error (FileExistsError): {e}")
    except FileNotFoundError as e:
        print(f"Demo error (FileNotFoundError): {e}")
    except ValueError as e:
        print(f"Demo error (ValueError): {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Optional: Clean up the test project directory after script execution
        # Comment out if you want to inspect the created files/directories.
        # print(f"\nCleaning up '{TEST_PROJECT_NAME}' directory post-test...")
        # if Path(TEST_PROJECT_NAME).exists():
        #     shutil.rmtree(TEST_PROJECT_NAME)
        #     print(f"'{TEST_PROJECT_NAME}' directory cleaned up.")
        pass

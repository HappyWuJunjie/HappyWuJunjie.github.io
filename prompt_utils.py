import json
import os
from pathlib import Path

# Attempt to import dependencies for the __main__ block.
# The functions themselves do not depend on these, only the demo.
try:
    from project import create_project
except ImportError:
    print("Warning: project.py not found. create_project function will not be available for the demo.")
    def create_project(project_name: str, base_path: str = '.'):
        print(f"Mock create_project called for {project_name} at {base_path}.")
        project_dir = Path(base_path) / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "outline.md").touch()
        (project_dir / "prompts.json").touch() # Crucial for some tests
        (project_dir / "nodes").mkdir(exist_ok=True)
        (project_dir / "activity_log.txt").touch()

try:
    from outline import add_outline_item, get_outline_items
except ImportError:
    print("Warning: outline.py not found. Outline functions will not be available for the demo.")
    def add_outline_item(project_path: str, item_text: str, is_main_heading: bool = True):
        print(f"Mock add_outline_item called for {project_path} with text '{item_text}'.")
    def get_outline_items(project_path: str) -> list[str]:
        print(f"Mock get_outline_items called for {project_path}. Returning predefined list.")
        return ["Mocked Item 1", "Mocked Item 2"]


def update_base_prompts(project_path: str, prompts_dict: dict):
    """
    Saves or overwrites the prompts_dict to prompts.json in the project_path.
    """
    proj_path = Path(project_path)
    if not proj_path.exists() or not proj_path.is_dir():
        # The original instruction implies project_path must exist.
        # If prompts.json doesn't exist, it's created. If it does, it's overwritten.
        # This means we don't create project_path itself here.
        raise FileNotFoundError(f"Project directory '{project_path}' not found or is not a directory.")

    prompts_file = proj_path / "prompts.json"

    try:
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_dict, f, indent=4)
    except IOError as e:
        print(f"Error writing to prompts.json: {e}")
        # Depending on desired behavior, could re-raise or handle more gracefully.
        # For now, printing error. The function doesn't explicitly return success/failure.

def get_prompts(project_path: str) -> dict:
    """
    Reads prompts.json and returns it as a dictionary.
    Returns an empty dictionary if the file doesn't exist, or if an error occurs.
    """
    prompts_file = Path(project_path) / "prompts.json"

    if not prompts_file.exists():
        return {}

    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except IOError as e:
        print(f"IOError reading prompts.json: {e}. Returning empty dict.")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError parsing prompts.json: {e}. Returning empty dict.")
        return {}

DEFAULT_AI_PROMPT = "You are a helpful assistant. Please respond to the user's query."

def construct_ai_prompt(
    base_prompt_key: str,
    project_path: str,
    user_query: str,
    previous_node_summary: str | None = None,
    current_outline: list[str] | None = None
) -> str:
    """
    Constructs a detailed AI prompt string.
    """
    prompts_dict = get_prompts(project_path)
    base_prompt = prompts_dict.get(base_prompt_key, DEFAULT_AI_PROMPT)

    assembled_prompt_parts = [base_prompt]

    if current_outline: # Check if list is not None and not empty
        outline_str = "\n".join([f"- {item}" for item in current_outline])
        assembled_prompt_parts.append(f"\nCurrent Learning Outline:\n{outline_str}")

    if previous_node_summary and previous_node_summary.strip(): # Check if string is not None and not empty/whitespace
        assembled_prompt_parts.append(f"\nSummary of previous lesson:\n{previous_node_summary}")

    assembled_prompt_parts.append(f"\nUser Query:\n{user_query}")

    return "\n".join(assembled_prompt_parts)


if __name__ == '__main__':
    TEST_PROJECT_NAME_PROMPTS = "TestProjectForPrompts"
    import shutil
    if Path(TEST_PROJECT_NAME_PROMPTS).exists():
        print(f"Cleaning up existing '{TEST_PROJECT_NAME_PROMPTS}' directory...")
        shutil.rmtree(TEST_PROJECT_NAME_PROMPTS)
    
    # Setup a secondary project for testing missing prompts.json
    TEST_PROJECT_NO_PROMPTS = "TestProjectNoPrompts"
    if Path(TEST_PROJECT_NO_PROMPTS).exists():
        shutil.rmtree(TEST_PROJECT_NO_PROMPTS)

    try:
        print(f"Attempting to create project: {TEST_PROJECT_NAME_PROMPTS}")
        create_project(TEST_PROJECT_NAME_PROMPTS) # From project.py
        project_prompts_path = Path(TEST_PROJECT_NAME_PROMPTS)
        print(f"Project '{TEST_PROJECT_NAME_PROMPTS}' created.\n")

        # 1. Test get_prompts on a project before prompts.json is created
        print(f"Attempting to create project: {TEST_PROJECT_NO_PROMPTS}")
        create_project(TEST_PROJECT_NO_PROMPTS)
        project_no_prompts_path = Path(TEST_PROJECT_NO_PROMPTS)
        print(f"Project '{TEST_PROJECT_NO_PROMPTS}' created for testing empty prompts.\n")
        
        print(f"Getting prompts from '{TEST_PROJECT_NO_PROMPTS}' (should be empty dict)...")
        prompts_before_update = get_prompts(str(project_no_prompts_path))
        print(f"Retrieved prompts: {prompts_before_update}")
        assert prompts_before_update == {}, f"Expected empty dict, got {prompts_before_update}"
        print("Successfully got empty dict for non-existent prompts.json.\n")


        # 2. Demonstrate update_base_prompts
        print(f"Updating base prompts for '{TEST_PROJECT_NAME_PROMPTS}'...")
        sample_prompts = {
            "explain_topic": "Explain the topic of {topic} in a clear and concise manner, suitable for a beginner.",
            "summarize_lesson": "Based on the preceding text, provide a brief summary of the key concepts learned in this lesson.",
            "generate_questions": "Generate 3 insightful questions based on the following text: {text}"
        }
        update_base_prompts(str(project_prompts_path), sample_prompts)
        print("Base prompts updated.\n")

        # 3. Demonstrate get_prompts
        print(f"Getting prompts from '{TEST_PROJECT_NAME_PROMPTS}'...")
        retrieved_prompts = get_prompts(str(project_prompts_path))
        print(f"Retrieved prompts: {json.dumps(retrieved_prompts, indent=2)}")
        assert retrieved_prompts == sample_prompts, "Retrieved prompts do not match sample prompts."
        print("Successfully retrieved and verified prompts.\n")

        # 4. Setup for construct_ai_prompt: Add outline items
        print(f"Adding outline items to '{TEST_PROJECT_NAME_PROMPTS}'...")
        add_outline_item(str(project_prompts_path), "Module 1: Basics")
        add_outline_item(str(project_prompts_path), "Module 2: Intermediate")
        add_outline_item(str(project_prompts_path), "Module 3: Advanced")
        current_outline_items = get_outline_items(str(project_prompts_path))
        print(f"Current outline items: {current_outline_items}\n")

        # 5. Simulate previous node summary
        previous_summary = "In the previous lesson, we covered the foundational concepts of Subject Y."

        # 6. Demonstrate construct_ai_prompt - full version
        print("Constructing AI prompt (full version)...")
        user_query_1 = "What is the main challenge in Module 2?"
        ai_prompt_1 = construct_ai_prompt(
            base_prompt_key="explain_topic",
            project_path=str(project_prompts_path),
            user_query=user_query_1,
            previous_node_summary=previous_summary,
            current_outline=current_outline_items
        )
        print("Constructed AI Prompt 1:\n--------------------------\n" + ai_prompt_1 + "\n--------------------------\n")
        assert "Explain the topic of {topic}" in ai_prompt_1
        assert "Current Learning Outline:" in ai_prompt_1
        assert "- Module 1: Basics" in ai_prompt_1
        assert "Summary of previous lesson:" in ai_prompt_1
        assert previous_summary in ai_prompt_1
        assert f"User Query:\n{user_query_1}" in ai_prompt_1

        # 7. Demonstrate construct_ai_prompt - no previous summary
        print("Constructing AI prompt (no previous summary)...")
        user_query_2 = "Can you elaborate on Module 1?"
        ai_prompt_2 = construct_ai_prompt(
            base_prompt_key="explain_topic",
            project_path=str(project_prompts_path),
            user_query=user_query_2,
            current_outline=current_outline_items
            # previous_node_summary is None by default
        )
        print("Constructed AI Prompt 2:\n--------------------------\n" + ai_prompt_2 + "\n--------------------------\n")
        assert "Summary of previous lesson:" not in ai_prompt_2

        # 8. Demonstrate construct_ai_prompt - no outline
        print("Constructing AI prompt (no outline)...")
        user_query_3 = "Summarize this for me."
        ai_prompt_3 = construct_ai_prompt(
            base_prompt_key="summarize_lesson",
            project_path=str(project_prompts_path),
            user_query=user_query_3,
            previous_node_summary=previous_summary
            # current_outline is None by default
        )
        print("Constructed AI Prompt 3:\n--------------------------\n" + ai_prompt_3 + "\n--------------------------\n")
        assert "Current Learning Outline:" not in ai_prompt_3

        # 9. Demonstrate construct_ai_prompt - invalid base_prompt_key (uses default)
        print("Constructing AI prompt (invalid base_prompt_key)...")
        user_query_4 = "Tell me a joke."
        ai_prompt_4 = construct_ai_prompt(
            base_prompt_key="non_existent_key",
            project_path=str(project_prompts_path),
            user_query=user_query_4
        )
        print("Constructed AI Prompt 4:\n--------------------------\n" + ai_prompt_4 + "\n--------------------------\n")
        assert DEFAULT_AI_PROMPT in ai_prompt_4
        assert f"User Query:\n{user_query_4}" in ai_prompt_4

        # 10. Test update_base_prompts with non-existent project path
        print("Testing update_base_prompts with non-existent project path...")
        try:
            update_base_prompts("NonExistentProjectForPrompts", {"key": "value"})
        except FileNotFoundError as e:
            print(f"Caught expected error: {e}\n")
        
        print("\nAll demonstrations finished.")

    except FileNotFoundError as e:
        print(f"Demo error (FileNotFoundError): {e}")
    except AssertionError as e:
        print(f"Demo assertion error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print(f"\nCleaning up '{TEST_PROJECT_NAME_PROMPTS}' directory post-test...")
        if Path(TEST_PROJECT_NAME_PROMPTS).exists():
            shutil.rmtree(TEST_PROJECT_NAME_PROMPTS)
        print(f"Cleaning up '{TEST_PROJECT_NO_PROMPTS}' directory post-test...")
        if Path(TEST_PROJECT_NO_PROMPTS).exists():
            shutil.rmtree(TEST_PROJECT_NO_PROMPTS)
        print("Cleanup complete.")

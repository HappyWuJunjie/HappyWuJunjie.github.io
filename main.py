import os
import shutil
from pathlib import Path

# Import functions from other modules
try:
    from project import create_project
    from logger import log_activity
    from outline import add_outline_item, get_outline_items
    from node import (
        create_node,
        save_chat_message,
        save_notes,
        save_summary,
        get_previous_node_summary, # Not explicitly used in this main sequence but good for completeness
        _sanitize_title as sanitize_node_title # For potential direct use, though not in current plan
    )
    from prompt_utils import update_base_prompts, construct_ai_prompt
except ImportError as e:
    print(f"Error importing necessary modules: {e}")
    print("Please ensure all required .py files (project.py, logger.py, outline.py, node.py, prompt_utils.py) are in the same directory.")
    exit(1)

def run_learning_session():
    """
    Runs a simulated AI-assisted learning session.
    """
    project_name = "MyAIDrivenLearning"
    base_dir = "learning_projects"
    project_path = Path(base_dir) / project_name

    # 1. Clean up existing project directory for a fresh demo run
    print(f"Attempting to clean up existing project directory: {project_path}")
    try:
        if project_path.exists():
            shutil.rmtree(project_path)
            print(f"Removed existing project directory: {project_path}")
    except OSError as e:
        print(f"Error removing directory {project_path}: {e}. Please check permissions or close open files.")
        return # Exit if cleanup fails critically

    print("-" * 50)

    # 2. Set up a Project
    try:
        print(f"Creating project: {project_name} in {base_dir}...")
        create_project(project_name, base_path=base_dir) # Corrected base_dir to base_path
        print(f"Project '{project_name}' created successfully at {project_path}.\n")
    except FileExistsError:
        print(f"Project directory '{project_path}' already exists. Proceeding with existing project.\n")
    except Exception as e:
        print(f"Could not create project: {e}")
        return

    # 3. Log Initial Activity
    log_activity(str(project_path), "Starting new learning session.")
    print("Initial activity logged.\n")

    # 4. Define and Update Base Prompts
    prompts_dict = {
        "general_query": "You are an expert tutor. Your goal is to explain the current topic clearly and concisely. Consider the user's learning outline and the summary of the previous lesson if available. Help the user understand: {query}",
        "summarize_node": "Based on our discussion and my notes for this node, please provide a concise summary of the key concepts learned."
    }
    update_base_prompts(str(project_path), prompts_dict)
    print("Base prompts updated.\n")

    # 5. Create Learning Outline
    print("Creating learning outline...")
    outline_topics = ["Introduction to Python", "Data Types and Variables", "Control Flow in Python"]
    for topic in outline_topics:
        add_outline_item(str(project_path), topic, is_main_heading=True)
        log_activity(str(project_path), f"Added main outline topic: {topic}")
    
    # Add a sub-item
    # Assuming "Introduction to Python" is the first topic and we want to add a sub-item to it.
    # outline.md structure will be:
    # # Introduction to Python
    #   - Basic Syntax
    # # Data Types and Variables
    # # Control Flow
    # For this to be robust, one might need to specify which main topic the sub-item belongs to.
    # The current add_outline_item just appends. For a structured sub-item,
    # one might need more context or edit the file more directly.
    # For this demo, we just append it; it will appear after "Control Flow".
    # To make it a true sub-item visually in the .md, it would need to be inserted.
    # Let's add it as specified, which means it will be appended.
    # A better add_outline_item might take a parent_heading argument.
    # For now, we'll add it and it will be a sub-item at the end of the current list of items.
    # Or, to make it a sub-item of "Introduction to Python", we can re-add the main heading then the sub-item.
    # The current add_outline_item simply appends. For the sake of this demo, this is fine.
    # It will look like:
    # # Topic 1
    # # Topic 2
    # # Topic 3
    #   - Sub item
    # This is how the current outline.py's add_outline_item works.
    sub_item_text = "Core Syntax and Structure"
    add_outline_item(str(project_path), sub_item_text, is_main_heading=False)
    log_activity(str(project_path), f"Added sub-outline item: {sub_item_text} (intended for 'Introduction to Python')")
    print("Learning outline created.\n")

    # 6. Retrieve and Display Outline
    main_topics_from_outline = get_outline_items(str(project_path)) # This gets only '# ' items
    print("Current Learning Outline (Main Topics):")
    for topic in main_topics_from_outline:
        print(f"- {topic}")
    print("-" * 50 + "\n")

    # 7. Simulate Learning in Nodes
    previous_summary = None
    # We will use the `main_topics_from_outline` as the basis for node creation.
    
    for i, node_title in enumerate(main_topics_from_outline):
        current_node_index = i
        print(f"\nProcessing Node {current_node_index + 1}: '{node_title}'")
        log_activity(str(project_path), f"Starting node: {node_title}")

        try:
            node_path = create_node(str(project_path), node_title)
            print(f"Node '{node_title}' created at {node_path}.")
        except FileExistsError:
            print(f"Node '{node_title}' already exists. Continuing with existing node.")
            # If node exists, we still need its path for other operations.
            # node.create_node raises error, so get path separately if allowing existing.
            # For this demo, create_node will fail if it exists.
            # A better workflow: check existence, then create or get path.
            # Let's assume for fresh run, it won't exist. If it does, current script will stop here for that node.
            # The task says "Handle FileExistsError by printing a message and continuing",
            # so we should catch and then get path.
            # Modifying create_node to return path even if exists or adding get_node_path here:
            from node import get_node_path
            node_path = get_node_path(str(project_path), node_title) # Get path if it already exists
            if not node_path.exists(): # Should not happen if FileExistsError was for this node
                print(f"Error: Node '{node_title}' reported as existing, but path not found: {node_path}")
                continue # skip to next node

        # Simulate a User Query
        user_query = f"Tell me more about {node_title}. What are the key aspects?"
        
        # Construct the AI prompt
        # The current_outline passed to construct_ai_prompt should ideally be all items, not just main topics.
        # For now, using main_topics_from_outline as per current get_outline_items capability.
        prompt = construct_ai_prompt(
            base_prompt_key="general_query",
            project_path=str(project_path),
            user_query=user_query,
            previous_node_summary=previous_summary,
            current_outline=main_topics_from_outline # Ideally, this would include sub-items too
        )
        print(f"\n--- AI Prompt for {node_title} ---")
        print(prompt)

        ai_response = f"This is a detailed explanation regarding {node_title}. It covers A, B, and C, building upon concepts from the previous lesson if applicable."
        print(f"--- Simulated AI Response ---")
        print(ai_response)

        # Save Interaction
        save_chat_message(str(project_path), node_title, "user", user_query)
        save_chat_message(str(project_path), node_title, "ai", ai_response)
        print("Chat interaction saved.")

        # Simulate Note-Taking
        node_notes = f"My personal notes for {node_title}:\n- AI mentioned: {ai_response[:70]}...\n- I need to explore concept B further.\n- Connect this to real-world example X."
        save_notes(str(project_path), node_title, node_notes)
        log_activity(str(project_path), f"Notes saved for node: {node_title}")
        print("Notes saved.")

        # Simulate Summary Generation
        current_summary = f"Summary for {node_title}: This node explained the core ideas of {node_title}, focusing on A, B, C. Important for next steps."
        save_summary(str(project_path), node_title, current_summary)
        log_activity(str(project_path), f"Summary saved for node: {node_title}")
        print("Summary saved.")
        
        previous_summary = current_summary # Update for the next iteration

        print(f"--- Completed Node: {node_title} ---")

    # 8. Final Log Message
    log_activity(str(project_path), "Learning session finished.")
    print("\n" + "=" * 50)
    print("Learning session simulation complete.")
    print(f"Project data saved in: {project_path}")
    print(f"Activity log: {project_path / 'activity_log.txt'}")
    print("Review the directory structure and files to see the results.")
    print("=" * 50)

if __name__ == '__main__':
    run_learning_session()

# AI-Assisted Learning Notes Framework

## Overview/Description

This project provides a backend framework for a note-taking application designed to integrate with AI for structured, project-based learning. It allows users to organize their learning into projects, define an outline, and then work through "nodes" (topics or chapters) with dedicated spaces for chat interactions (simulated AI), personal notes, and summaries. The system is designed to construct contextual prompts for AI interaction by incorporating the learning outline and summaries from previous nodes.

**Key Features:**

*   **Project-Based Organization:** Learning materials and notes are organized within distinct projects.
*   **Learning Outline:** Users define their learning path in an `outline.md` file within each project.
*   **Node-Based Learning:** Each topic or chapter in the outline can be a "node" with its own:
    *   `chat_history.jsonl`: For storing (simulated) AI interactions.
    *   `notes.md`: For user-generated notes.
    *   `summary.txt`: For storing a summary of the node's content.
*   **Contextual AI Prompt Construction:** The system can build detailed prompts for AI interaction, leveraging:
    *   Base prompts stored in `prompts.json`.
    *   The overall learning outline.
    *   The summary of the previously completed node.
*   **Activity Logging:** All significant actions, such as project creation, node processing, and outline modifications, are logged to `activity_log.txt` within each project.

## Project Structure

The project consists of the following main Python files:

*   `main.py`: The main application script that demonstrates an end-to-end workflow of creating a project, adding to the outline, and simulating node-based learning.
*   `project.py`: Manages the creation and basic structure of new learning projects.
*   `node.py`: Handles operations related to individual learning nodes, such as creating node directories, saving chat messages, notes, and summaries.
*   `outline.py`: Manages the `outline.md` file, allowing items to be added and main topics to be retrieved.
*   `prompt_utils.py`: Responsible for managing base AI prompts (stored in `prompts.json`) and constructing detailed prompts for AI interaction.
*   `logger.py`: Provides a centralized logging function to record activities within a project.
*   `test_*.py`: A suite of unit tests for each module (`test_project.py`, `test_logger.py`, `test_outline.py`, `test_node.py`, `test_prompt_utils.py`) to ensure functionality.

**Directory Structure for a Created Project:**

When a new project (e.g., `MyLearningProject`) is created, it will have the following structure:

```
MyLearningProject/
├── outline.md
├── prompts.json
├── activity_log.txt
└── nodes/
    ├── (sanitized_node_title_1)/
    │   ├── chat_history.jsonl
    │   ├── notes.md
    │   └── summary.txt
    └── (sanitized_node_title_2)/
        ├── chat_history.jsonl
        ├── notes.md
        └── summary.txt
        ...
```

## Setup and Installation

**Prerequisites:**

*   Python 3.x (developed and tested with Python 3.10+)

**Setup:**

1.  **Download/Clone:** Download the Python files (`.py`) or clone the repository if it's hosted (e.g., using Git).
    ```bash
    # Example if using Git:
    # git clone <repository_url>
    # cd <repository_directory>
    ```
2.  **Dependencies:** The project currently uses only Python's standard library, so no external dependencies need to be installed via `pip`. All required modules are part_of this package.

## How to Run

1.  **Run the Main Demonstration:**
    To see a demonstration of the framework in action, execute `main.py`:
    ```bash
    python main.py
    ```
    This script will:
    *   Create a sample project named "MyAIDrivenLearning" inside a `learning_projects` directory.
    *   Populate it with a sample outline, prompts, and simulate node interactions.
    *   Log all activities.
    *   You can inspect the `learning_projects/MyAIDrivenLearning` directory to see the generated files and structure.

2.  **Run Unit Tests:**
    To ensure all modules are working correctly, you can run the unit tests:
    ```bash
    python -m unittest discover -v
    ```
    This command will discover and run all tests located in files named `test_*.py`.

## How It Works (Brief Technical Workflow)

1.  **Project Initialization:** A user (or script like `main.py`) initiates a new project using `project.create_project()`. This sets up the basic directory structure and essential files like `outline.md`, `prompts.json`, and `activity_log.txt`.
2.  **Outline Definition:** The learning outline is manually defined by adding main topics and sub-items to the `outline.md` file using functions from `outline.py`.
3.  **Node-by-Node Interaction:** The user progresses through the learning material node by node (based on the outline).
    *   For each node, `node.create_node()` sets up the specific subdirectory.
4.  **AI Prompt Construction:** When interacting with the (simulated) AI for a node:
    *   `prompt_utils.construct_ai_prompt()` builds a detailed prompt. This prompt incorporates:
        *   A base prompt selected from `prompts.json`.
        *   The overall learning outline (from `outline.md`).
        *   The summary of the previously completed learning node (from `summary.txt` of the previous node).
        *   The specific user query.
5.  **Saving Information:**
    *   The user's query and the AI's response are saved to `chat_history.jsonl` within the current node's directory using `node.save_chat_message()`.
    *   The user's personal notes are saved to `notes.md` using `node.save_notes()`.
    *   A summary of the node's content (simulated as AI-generated or user-input) is saved to `summary.txt` using `node.save_summary()`.
6.  **Logging:** All significant actions (project creation, outline changes, node operations, etc.) are logged with timestamps to `activity_log.txt` by `logger.log_activity()`.

## Future Enhancements

*   **Actual AI Integration:** Connect the framework to a real AI model (e.g., via OpenAI API, Hugging Face Transformers) to replace the simulated AI responses.
*   **GUI Implementation:** Develop a graphical user interface (e.g., using Tkinter, PyQt, or a web framework like Flask/Django) for easier interaction.
*   **Advanced Outline Management:**
    *   Support for hierarchical outlines (nested topics).
    *   Functions to easily reorder, edit, or delete outline items.
*   **AI-Powered Content Generation:**
    *   Utilize AI to help generate initial learning outlines based on a topic.
    *   Employ AI to automatically summarize node content or chat interactions.
*   **Improved Node Navigation:** Implement explicit linking or sequencing between nodes.
*   **Search and Retrieval:** Add functionality to search across notes, summaries, and chat histories within a project.

import unittest
import os
import shutil
from pathlib import Path
import json

# Add project root to sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from prompt_utils import update_base_prompts, get_prompts, construct_ai_prompt, DEFAULT_AI_PROMPT
from project import create_project
from outline import add_outline_item, get_outline_items # For testing prompt construction with outline

class TestPromptUtils(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = Path("temp_test_prompt_utils_base")
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        self.test_base_dir.mkdir(parents=True, exist_ok=True)

        self.project_name = "PromptUtilsTestProject"
        create_project(self.project_name, base_path=str(self.test_base_dir))
        self.project_path = self.test_base_dir / self.project_name
        self.prompts_file_path = self.project_path / "prompts.json"

    def tearDown(self):
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)

    def test_update_base_prompts_creates_and_writes(self):
        sample_prompts = {"key1": "prompt1", "key2": "prompt2"}
        update_base_prompts(str(self.project_path), sample_prompts)
        
        self.assertTrue(self.prompts_file_path.exists())
        with open(self.prompts_file_path, 'r') as f:
            content = json.load(f)
        self.assertEqual(content, sample_prompts)

    def test_update_base_prompts_overwrites(self):
        prompts1 = {"key1": "old_prompt"}
        update_base_prompts(str(self.project_path), prompts1)

        prompts2 = {"key2": "new_prompt"}
        update_base_prompts(str(self.project_path), prompts2) # Should overwrite

        with open(self.prompts_file_path, 'r') as f:
            content = json.load(f)
        self.assertEqual(content, prompts2)
        self.assertNotIn("key1", content)

    def test_update_base_prompts_non_existent_project_path(self):
        non_existent_path = str(self.test_base_dir / "GhostProjectPrompts")
        with self.assertRaises(FileNotFoundError):
            update_base_prompts(non_existent_path, {"key": "value"})

    def test_get_prompts_successful_read(self):
        sample_prompts = {"read_key": "read_value"}
        update_base_prompts(str(self.project_path), sample_prompts)
        
        retrieved_prompts = get_prompts(str(self.project_path))
        self.assertEqual(retrieved_prompts, sample_prompts)

    def test_get_prompts_file_not_found(self):
        # Ensure prompts.json does not exist (it's created by create_project, so delete it)
        if self.prompts_file_path.exists():
            self.prompts_file_path.unlink()
        self.assertFalse(self.prompts_file_path.exists())
        
        retrieved_prompts = get_prompts(str(self.project_path))
        self.assertEqual(retrieved_prompts, {})

    def test_get_prompts_invalid_json(self):
        with open(self.prompts_file_path, 'w') as f:
            f.write("this is not valid json {")
        
        retrieved_prompts = get_prompts(str(self.project_path))
        self.assertEqual(retrieved_prompts, {}) # Expect empty dict on JSONDecodeError

    def test_get_prompts_empty_json_file(self):
        # create_project touches prompts.json making it empty.
        # An empty file is not valid JSON.
        self.assertTrue(self.prompts_file_path.exists()) # created by setUp
        with open(self.prompts_file_path, 'w') as f: # Ensure it's truly empty
            f.write("")

        retrieved_prompts = get_prompts(str(self.project_path))
        self.assertEqual(retrieved_prompts, {}) # Expect empty dict on JSONDecodeError

    def test_construct_ai_prompt_default_prompt(self):
        user_query = "What is AI?"
        prompt = construct_ai_prompt(
            base_prompt_key="non_existent_key",
            project_path=str(self.project_path),
            user_query=user_query
        )
        self.assertIn(DEFAULT_AI_PROMPT, prompt)
        self.assertIn(f"\nUser Query:\n{user_query}", prompt)

    def test_construct_ai_prompt_with_base_key(self):
        my_prompts = {"custom_intro": "You are a Socratic tutor. Query: {query}"}
        update_base_prompts(str(self.project_path), my_prompts)
        user_query = "Explain quantum physics."
        
        prompt = construct_ai_prompt(
            base_prompt_key="custom_intro",
            project_path=str(self.project_path),
            user_query=user_query
        )
        self.assertIn(my_prompts["custom_intro"], prompt) # Base prompt should be there
        self.assertNotIn(DEFAULT_AI_PROMPT, prompt) # Default should not
        self.assertIn(f"\nUser Query:\n{user_query}", prompt)


    def test_construct_ai_prompt_with_outline(self):
        user_query = "Next topic?"
        outline_items_text = ["Topic A", "Topic B"]
        
        # Clear outline.md and add items
        with open(self.project_path / "outline.md", 'w') as f: f.write("")
        for item in outline_items_text:
            add_outline_item(str(self.project_path), item, is_main_heading=True)
        
        # Fetch items using get_outline_items to pass to construct_ai_prompt
        fetched_outline_for_prompt = get_outline_items(str(self.project_path))

        prompt = construct_ai_prompt(
            base_prompt_key="any_key", # Using default for simplicity here
            project_path=str(self.project_path),
            user_query=user_query,
            current_outline=fetched_outline_for_prompt
        )
        self.assertIn("\nCurrent Learning Outline:\n", prompt)
        for item_text in outline_items_text:
            self.assertIn(f"- {item_text}", prompt)

    def test_construct_ai_prompt_with_previous_summary(self):
        user_query = "Building on that..."
        summary_text = "Previously, we discussed X."
        prompt = construct_ai_prompt(
            base_prompt_key="any_key",
            project_path=str(self.project_path),
            user_query=user_query,
            previous_node_summary=summary_text
        )
        self.assertIn("\nSummary of previous lesson:\n", prompt)
        self.assertIn(summary_text, prompt)

    def test_construct_ai_prompt_with_all_elements(self):
        custom_prompts = {"full_prompt_test": "Guide on {topic} considering prior work and outline."}
        update_base_prompts(str(self.project_path), custom_prompts)
        
        user_query = "What about advanced topic Z?"
        outline_items_text = ["Intro", "Advanced Topic Z"]
        with open(self.project_path / "outline.md", 'w') as f: f.write("") # Clear
        for item in outline_items_text: add_outline_item(str(self.project_path), item, True)
        fetched_outline = get_outline_items(str(self.project_path))

        summary_text = "We just covered Intro to Y."

        prompt = construct_ai_prompt(
            base_prompt_key="full_prompt_test",
            project_path=str(self.project_path),
            user_query=user_query,
            current_outline=fetched_outline,
            previous_node_summary=summary_text
        )
        self.assertIn(custom_prompts["full_prompt_test"], prompt)
        self.assertIn("\nCurrent Learning Outline:\n", prompt)
        self.assertIn("- Advanced Topic Z", prompt)
        self.assertIn("\nSummary of previous lesson:\n", prompt)
        self.assertIn(summary_text, prompt)
        self.assertIn(f"\nUser Query:\n{user_query}", prompt)

    def test_construct_ai_prompt_empty_optional_strings_and_lists(self):
        user_query = "Test query."
        prompt_with_empty_optionals = construct_ai_prompt(
            base_prompt_key="any_key",
            project_path=str(self.project_path),
            user_query=user_query,
            previous_node_summary="", # Empty string
            current_outline=[]       # Empty list
        )
        self.assertNotIn("\nCurrent Learning Outline:\n", prompt_with_empty_optionals)
        self.assertNotIn("\nSummary of previous lesson:\n", prompt_with_empty_optionals)
        self.assertIn(DEFAULT_AI_PROMPT, prompt_with_empty_optionals) # Assuming 'any_key' is not in prompts.json
        self.assertIn(f"\nUser Query:\n{user_query}", prompt_with_empty_optionals)

if __name__ == '__main__':
    unittest.main()

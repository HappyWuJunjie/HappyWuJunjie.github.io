import json
import os
from typing import List, Dict, TypedDict

# Get the directory of the current file (utils.py)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the root directory (multi_model_app)
ROOT_DIR = os.path.dirname(APP_DIR)

API_KEYS_FILE = os.path.join(ROOT_DIR, "config", "api_keys.json")
MODELS_CONFIG_FILE = os.path.join(ROOT_DIR, "config", "models_config.json")

class Message(TypedDict):
    role: str
    content: str

class Conversation:
    def __init__(self, model_name: str, context_length: int):
        self.model_name = model_name
        self.context_length = context_length # Max number of messages for now
        self.messages: List[Message] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self.enforce_context_limit()

    def get_messages(self) -> List[Message]:
        return self.messages

    def enforce_context_limit(self):
        # Simple truncation: keep the most recent 'self.context_length' messages
        if len(self.messages) > self.context_length:
            self.messages = self.messages[-self.context_length:]
    
    def clear(self):
        self.messages = []

class Model:
    def __init__(self, name: str, api_key_name: str, context_length: int):
        self.name: str = name
        self.api_key_name: str = api_key_name
        self.context_length: int = context_length
        self.client = None # Will be initialized in main.py
        # Initialize conversation with the model's specific context_length
        self.conversation = Conversation(model_name=name, context_length=self.context_length)

    def __repr__(self) -> str:
        return f"Model(name='{self.name}', context_length={self.context_length})"

def load_api_key(key_name: str) -> str:
    try:
        with open(API_KEYS_FILE, 'r') as f:
            keys = json.load(f)
        api_key = keys.get(key_name)
        if not api_key:
            raise KeyError(f"Key '{key_name}' not found in {API_KEYS_FILE}")
        if "YOUR_OPENAI_API_KEY_HERE" in api_key or not api_key.strip():
            # Return the placeholder/empty key, main.py will handle warnings
            return api_key 
        return api_key
    except FileNotFoundError:
        raise FileNotFoundError(f"API keys file not found at {API_KEYS_FILE}.")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from {API_KEYS_FILE}.")

def load_models_config() -> dict:
    try:
        with open(MODELS_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Models config file not found at {MODELS_CONFIG_FILE}.")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from {MODELS_CONFIG_FILE}.")

def get_latest_responses_for_summary(model_objects: Dict[str, Model]) -> Dict[str, str]:
    """
    Collects the last assistant response from each model's conversation.
    Args:
        model_objects: A dictionary of Model objects, keyed by model name.
    Returns:
        A dictionary where keys are model names and values are the last assistant responses.
        Returns an empty string for a model if no assistant response is found.
    """
    latest_responses = {}
    for model_name, model_obj in model_objects.items():
        last_assistant_response = ""
        # Ensure conversation and messages exist
        if hasattr(model_obj, 'conversation') and model_obj.conversation and hasattr(model_obj.conversation, 'get_messages'):
            for message in reversed(model_obj.conversation.get_messages()):
                if message["role"] == "assistant":
                    last_assistant_response = message["content"]
                    break
        latest_responses[model_name] = last_assistant_response
    return latest_responses

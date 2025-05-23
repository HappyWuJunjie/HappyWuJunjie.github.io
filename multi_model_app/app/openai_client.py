# For OpenAI API interactions
import openai
from .utils import load_api_key

class OpenAIClient:
    def __init__(self, model_name: str, api_key: str = None, api_key_name: str = "openai_api_key"):
        self.model_name = model_name
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = load_api_key(api_key_name)
            except (FileNotFoundError, KeyError, ValueError) as e:
                raise ValueError(f"API key for model {model_name} (key name: {api_key_name}) could not be loaded: {e}")

        if not self.api_key or self.api_key == "YOUR_OPENAI_API_KEY_HERE" or not self.api_key.strip():
            raise ValueError(
                f"API key for {model_name} (key name: {api_key_name}) is missing, a placeholder, or empty. "
                f"Please provide a valid API key in config/api_keys.json or directly."
            )

        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except openai.OpenAIError as e: # Catching a more general OpenAI client init error
            raise ConnectionError(f"Failed to initialize OpenAI client for model {model_name}: {e}")


    def get_chat_completion(self, messages: list, stream: bool = False):
        """
        Gets a chat completion from the OpenAI API.

        Args:
            messages: A list of messages in OpenAI format.
            stream: Boolean flag to indicate streaming response.

        Returns:
            If stream is False, returns the content of the message.
            If stream is True, returns an iterator over response chunks.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages, # type: ignore
                stream=stream
            )

            if stream:
                def stream_generator():
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                return stream_generator()
            else:
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content
                else:
                    # Handle cases where the response might be empty or not as expected
                    return "Error: No content received from API."
        except openai.APIError as e:
            # Handle API errors (e.g., rate limits, server errors)
            print(f"OpenAI API error for model {self.model_name}: {e}")
            # Depending on desired behavior, you might re-raise, return a custom error message, etc.
            if stream:
                def error_stream():
                    yield f"Error: OpenAI API error - {e}"
                return error_stream()
            return f"Error: OpenAI API error - {e}"
        except Exception as e:
            # Handle other potential errors (e.g., network issues)
            print(f"An unexpected error occurred while communicating with OpenAI for model {self.model_name}: {e}")
            if stream:
                def error_stream():
                    yield f"Error: Unexpected error - {e}"
                return error_stream()
            return f"Error: Unexpected error - {e}"

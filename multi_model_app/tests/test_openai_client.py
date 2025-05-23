# Tests for the OpenAI client
import unittest
from app.openai_client import OpenAIClient

class TestOpenAIClient(unittest.TestCase):
    def test_client_initialization(self):
        client = OpenAIClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")

    def test_send_request(self):
        client = OpenAIClient(api_key="test_key")
        # This is a placeholder test, expand as functionality is added
        response = client.send_request(messages=[{"role": "user", "content": "Hello"}])
        self.assertIsNotNone(response)

if __name__ == "__main__":
    unittest.main()

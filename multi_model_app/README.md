# Multi-Model Conversation Application

This project is a Python application for interacting with multiple language models. It allows users to manage conversations with different models, configure model settings, and store API keys securely.

## Project Structure

- `app/`: Contains the main application logic.
  - `__init__.py`: Initializes the app package.
  - `main.py`: Main script to run the application.
  - `openai_client.py`: Handles interactions with the OpenAI API.
  - `utils.py`: Defines utility functions and data structures like `Conversation` and `Model`.
- `static/`: For static assets (e.g., CSS).
- `templates/`: For HTML templates.
- `config/`: Stores configuration files.
  - `models_config.json`: Configures models (names, context lengths, API key names).
  - `api_keys.json`: Stores API keys (gitignored).
- `tests/`: Contains unit tests.
  - `__init__.py`: Initializes the tests package.
  - `test_openai_client.py`: Tests for the OpenAI client.
- `.gitignore`: Specifies intentionally untracked files that Git should ignore.
- `requirements.txt`: Lists project dependencies.
- `README.md`: This file, providing an overview of the project.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd multi_model_app
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys:**
   - Rename `config/api_keys.json.example` to `config/api_keys.json`.
   - Add your API keys to `config/api_keys.json`.

5. **Run the application:**
   ```bash
   python app/main.py
   ```

## Usage

(To be added: Detailed instructions on how to use the application.)

## Testing

To run tests:
```bash
python -m unittest discover tests
```

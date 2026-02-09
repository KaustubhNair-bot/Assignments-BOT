# LLM Chat Interface

A Streamlit-based web application for interacting with Large Language Models (LLMs).

## Features

- **System Prompt Configuration**: Define the AI's behavior and role
- **User Prompt Input**: Enter questions or requests for the AI
- **Formatted Output Display**: View responses in multiple formats (Plain Text, Markdown, JSON)
- **Model Selection**: Choose from various LLM models
- **Adjustable Parameters**: Control temperature and max tokens
- **Conversation History**: Track and review past interactions
- **Responsive Design**: Clean, modern interface with sidebar configuration

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. **Configure Model Settings**: Use the sidebar to select model, temperature, and max tokens
2. **Set System Prompt**: Define how the AI should behave in the System Prompt text area
3. **Enter User Prompt**: Type your question or request in the User Prompt text area
4. **Generate Response**: Click "Generate Response" to get the AI's output
5. **View Results**: The response appears in the output section with multiple formatting options
6. **Review History**: Check the conversation history at the bottom of the page

## File Structure

```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # Environment variables (if needed)
```

## Customization

The app is designed to be easily extensible. You can:
- Add more model options to the `model_options` list
- Integrate actual LLM APIs (currently uses mock responses)
- Customize the UI styling and layout
- Add additional features like file uploads, export functionality, etc.

## Notes

- Currently uses mock responses for demonstration purposes
- To integrate with real LLM APIs, you'll need to add API keys and implement the actual API calls
- The app stores conversation history in session state only (not persistent)

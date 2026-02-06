# LLM Chat Interface

A clean and minimal Streamlit application for interacting with Groq's language models using custom system and user prompts.

## Features

- **Two-panel layout**: Input panel on the left, response panel on the right
- **System Prompt**: Set the context and behavior for the AI assistant
- **User Prompt**: Enter your questions or messages
- **Chat History**: Maintains conversation history using Streamlit session state
- **Error Handling**: Graceful handling of empty inputs and API errors
- **Environment Variables**: Secure API key management using .env files

## Project Structure

```
assignment_vibecode_GurkirtKaur/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .streamlit/secrets.toml  # Streamlit secrets configuration
├── .gitignore         # Git ignore file
└── README.md          # Project documentation
```

## Setup Instructions

### 1. Setup Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create the `.env` file and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Get a Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

1. **System Prompt (Optional)**: Enter a system prompt to define the AI assistant's behavior, personality, or context. For example:
   - "You are a helpful Python programming assistant."
   - "You are an expert in data science and machine learning."

2. **User Prompt**: Enter your actual question or message. This field is required.

3. **Send**: Click the "Send" button to submit both prompts to the Groq API.

4. **Output**: View the AI's response in the output panel on the right, along with the complete conversation history.

## Dependencies

- `streamlit==1.28.1`: Web application framework
- `groq==0.4.1`: Groq API client
- `python-dotenv==1.0.0`: Environment variable management

## Model Configuration

The application uses the `llama-3.1-8b-instant` model which provides a good balance of performance and speed. You can modify the model in the `get_llm_response()` function in `app.py` if needed.

## Error Handling

- **Missing API Key**: The app will display an error if the GROQ_API_KEY is not found in environment variables
- **Empty Inputs**: Validation ensures at least a user prompt is provided before sending
- **API Errors**: Network or API errors are caught and displayed gracefully

## Customization

You can easily customize the application by modifying:

- **Model**: Change the Groq model in the `get_llm_response()` function
- **UI Layout**: Modify the column ratios in the main layout
- **Styling**: Add custom CSS using `st.markdown()` with unsafe_allow_html=True
- **Additional Features**: Extend with file uploads, different models, or export functionality

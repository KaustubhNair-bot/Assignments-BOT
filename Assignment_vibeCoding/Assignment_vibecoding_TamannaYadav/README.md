# Prompt Engineering Playground

An interactive tool to experiment with system prompts, user prompts, and temperature settings using the Groq API.

## Features

- **Custom System Prompt** — Define additional context or persona for the AI
- **Custom User Prompt** — Enter your questions or tasks
- **Adjustable Temperature** — Control response creativity (0.0 to 2.0)
- **Model Selection** — Choose from multiple Groq models
- **Real-time LLM Response** — Fast inference powered by Groq

## Project Structure

```
project_root/
├── backend/
│   ├── __init__.py
│   ├── llm_handler.py       # Groq API calling logic
│   └── prompt.py            # Fixed developer instruction layer
├── frontend/
│   └── app.py               # Streamlit interface
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Create and activate a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

Copy the example environment file:

```bash
cp .env.example .env
```

Then open `.env` and add your real API key:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Get your API key from: https://console.groq.com/keys

### 4. Run the application

```bash
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`.

## Architecture Notes

This application uses a **three-layer prompt system**:

1. **Developer Instructions** (fixed) — Core behavior rules, safety guidelines, and output formatting defined in `backend/prompt.py`. These always apply and cannot be overridden by user input.

2. **User System Prompt** — Optional additional context or persona provided through the UI.

3. **User Message** — The actual question or task from the user.

This architecture mirrors how production LLM applications separate developer intent from user input, ensuring consistent behavior and quality.

## Available Models

- `llama-3.3-70b-versatile` — Llama 3.3 70B (default)
- `llama-3.1-8b-instant` — Llama 3.1 8B

> **Note:** Models may be deprecated over time. Check [Groq's deprecations page](https://console.groq.com/docs/deprecations) for the latest available models.

## License

MIT

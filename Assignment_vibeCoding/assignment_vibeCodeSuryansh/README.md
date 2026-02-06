# 🤖 AI Assistant - Groq Powered

A professional Streamlit application with Groq API integration for generating AI responses with customizable parameters.

## ✨ Features

- **🎯 Multiple Output Modes**: General, Coding, Research, and Web Search with auto-optimized temperature settings
- **🔑 Groq API Integration**: Uses latest models including LLaMA 3.1, Mixtral, and Gemma
- **🎨 Dark Mode UI**: Beautiful dark theme with orange accent colors inspired by OpenAI Playground
- **📊 Real-time Metrics**: Response time, history count, and current settings display
- **📜 Conversation History**: Save and reload previous conversations
- **🌡️ Temperature Control**: Adjustable creativity slider with mode-specific presets
- **📋 Copy Functionality**: Easy response copying to clipboard
- **🚀 Interactive Buttons**: Hover and click animations for better UX

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up API key** (choose one method):
   
   **Option A: Using .env file (Recommended)**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key:
   GROQ_API_KEY=your_actual_api_key_here
   ```
   
   **Option B: Enter manually in the app**
   - The app will prompt for API key in the sidebar
   
4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 🎮 Usage Guide

### Basic Workflow
1. **API Key Setup**: Either use .env file or enter manually in sidebar
2. **Select Model**: Choose from available Groq models
3. **Configure Input**:
   - Select output mode (auto-adjusts temperature)
   - Enter system prompt (AI's role/persona)
   - Enter user prompt (your question/request)
4. **Generate**: Click the orange "Generate Response" button
5. **View Results**: Response appears on the right side

### API Key Management
- **.env File**: Securely store your API key (recommended)
- **Manual Entry**: Type directly in the sidebar for quick testing
- **Visual Indicator**: See when API key is loaded from .env file
- **Security**: Your API key is masked in the UI

### Output Modes & Temperature Presets
- **General** (0.7): Balanced responses with markdown formatting and clear structure
- **Coding** (0.1): Precise code generation with syntax highlighting, examples, and best practices
- **Research** (0.3): Factual responses with headers, bullet points, tables, and source citations
- **Web Article** (0.5): Engaging content with H2/H3 headers, practical examples, and conversational tone
- **Interview** (0.4): Q&A format with sample answers, do's/don'ts tables, and preparation tips

### History Management
- **Automatic Saving**: Every conversation is automatically saved
- **Quick Load**: Click any history item to reload its settings
- **Storage**: Keeps last 50 conversations
- **Clear Option**: Remove all history with one click

## 🛠️ Available Models

- **LLaMA 3.3 70B Versatile**: Latest high-performance general model

## 🎨 Design Features

- **Dark Theme**: Easy on the eyes with gradient backgrounds
- **Orange Accents**: Vibrant buttons with hover effects
- **Glass Morphism**: Frosted glass effects for modern look
- **Responsive Layout**: Two-column design for optimal screen usage
- **Micro-interactions**: Smooth transitions and animations
- **Fixed Footer**: Always-visible metrics dashboard

## 📊 Metrics Display

- **History Count**: Number of saved conversations
- **Response Time**: API call duration in seconds
- **Temperature**: Current creativity setting
- **Mode**: Active output mode
- **Model**: Selected AI model

## 🔧 Customization

### Adding New Modes
Edit the `TEMPERATURE_PRESETS` dictionary in `app.py`:
```python
TEMPERATURE_PRESETS = {
    "General": 0.7,
    "Coding": 0.1,
    "Research": 0.3,
    "Web Search": 0.5,
    "Your New Mode": 0.6
}
```

### Adding New Models
Update the `GROQ_MODELS` dictionary:
```python
GROQ_MODELS = {
    "model-id": "Display Name",
    # Add more models
}
```

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Ensure your Groq API key is valid and has credits
2. **Slow Responses**: Try switching to a faster model like LLaMA 3.1 8B Instant
3. **No History**: Check if you have cookies enabled in your browser
4. **Styling Issues**: Clear browser cache and restart the app

### Error Messages
- **⚠️ API Error**: Check your API key and internet connection
- **❌ Error**: Verify Groq service status at status.groq.com

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

Made with ❤️ using [Streamlit](https://streamlit.io) & [Groq](https://groq.com)

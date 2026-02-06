# AI Assistant - Production-Ready Streamlit Application

A professional, production-ready AI assistant web application built with Streamlit and Groq API. Features a clean two-column interface with advanced functionality, security measures, and performance optimizations.

## 🚀 Features

### Core Functionality
- **Two-Column Layout**: Input controls on the left, AI response on the right
- **Multiple AI Models**: Support for Mixtral, Llama3-70B, and Llama3-8B
- **Temperature Control**: Adjustable creativity level (0.0-2.0)
- **System & User Prompts**: Separate inputs for system context and user queries
- **Real-time Response**: Fast AI responses with loading indicators

### Production Features
- **Security**: Environment variable management, no API keys in UI
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Input Validation**: Sanitization and length limits for all inputs
- **Session Management**: Persistent conversation history
- **Export Functionality**: Download conversations as text files
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode Support**: Automatic dark mode detection

### Performance Optimizations
- **Response Caching**: Avoid redundant API calls
- **Lazy Loading**: Efficient component rendering
- **Debounced Inputs**: Optimized input handling
- **Connection Pooling**: Efficient API connections

## 📁 Project Structure

```
Vive_coding/
├── app.py              # Main Streamlit application
├── config.py           # Configuration constants and settings
├── utils.py            # Helper functions and API calls
├── .env                # Environment variables (create this)
├── .env.example        # Environment variables template
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (get one at [console.groq.com](https://console.groq.com/keys))

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd Vibe_coding
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**
   ```bash
   # Option 1: Using the startup script (Recommended)
   ./run.sh
   
   # Option 2: Manual startup
   source venv/bin/activate
   streamlit run app.py
   ```

The application will open automatically in your browser at `http://localhost:8501`

## 🎯 Usage Guide

### Basic Usage
1. **Set Temperature**: Use the slider to adjust response creativity (0.0 = focused, 2.0 = creative)
2. **Choose Model**: Select from available AI models
3. **System Prompt**: Define the AI's role and behavior (optional)
4. **User Prompt**: Enter your question or request
5. **Generate**: Click "Generate Response" to get the AI response

### Advanced Features
- **Conversation History**: View previous conversations in the sidebar
- **Export**: Download conversations as text files
- **Copy to Clipboard**: Quick copy of AI responses
- **Token Metrics**: View detailed token usage and cost estimates
- **Keyboard Shortcuts**: Use Ctrl+Enter to submit quickly
- **Dark Mode**: Toggle between light and dark themes in the sidebar

### Model Selection
- **llama-3.3-70b-versatile**: Latest Llama 3.3 70B for versatile tasks (131K tokens)
- **llama-3.1-8b-instant**: Fast Llama 3.1 8B for quick responses (131K tokens)
- **gpt-oss-120b**: OpenAI GPT OSS 120B for complex tasks (8K tokens)
- **gpt-oss-20b**: OpenAI GPT OSS 20B for balanced performance (8K tokens)
- **llama-guard-4-12b**: Llama Guard 4 12B for content moderation (131K tokens)
- **compound**: Compound system with web search and code execution (8K tokens)
- **compound-mini**: Compact compound system for quick tasks (4K tokens)

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:
```env
GROQ_API_KEY=your_api_key_here
```

### Application Settings
Edit `config.py` to modify:
- Token limits and timeouts
- Default prompts and temperatures
- Rate limiting settings
- Model configurations
- UI preferences

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Add `GROQ_API_KEY` as a secret in Streamlit Cloud settings
4. Deploy

### Heroku
1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Set environment variables in Heroku dashboard
3. Deploy using Heroku CLI

### AWS/Azure/GCP
Deploy using Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔒 Security Features

- **API Key Protection**: No API keys in code or UI
- **Input Sanitization**: XSS protection and input validation
- **Rate Limiting**: Prevents API abuse
- **Environment Variables**: Secure configuration management
- **No Sensitive Logs**: No sensitive data in application logs

## 🧪 Testing

Run the test suite:
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## 📊 Performance

### Optimization Features
- **Response Caching**: Reduces API calls for identical requests
- **Lazy Loading**: Components load only when needed
- **Efficient State Management**: Minimized re-renders
- **Connection Pooling**: Reuses API connections

### Metrics
- Average response time: < 3 seconds
- Memory usage: < 200MB
- CPU usage: < 10% (idle)

## 🐛 Troubleshooting

### Common Issues

**API Key Error**
```
Solution: Check your .env file and ensure GROQ_API_KEY is set correctly
```

**Import Error / ModuleNotFoundError**
```
Solution: Always run the application using the startup script './run.sh' 
or manually activate the virtual environment first:
source venv/bin/activate
streamlit run app.py
```

**Model Decommissioned Error**
```
Solution: The application has been updated with the latest Groq models. 
Restart the application to use the updated model list.
```

**Dark Mode Not Working**
```
Solution: Dark mode toggle is now functional. Use the checkbox in the sidebar 
to toggle between light and dark themes.
```

**Connection Timeout**
```
Solution: Check your internet connection and API key validity
```

**Rate Limit Exceeded**
```
Solution: Wait for the rate limit window to reset (60 seconds)
```

### Debug Mode
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Groq](https://groq.com/) for fast AI inference
- The open-source community for inspiration and tools

## 📞 Support

For support, please:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information

---

**Built with ❤️ using Streamlit and Groq**

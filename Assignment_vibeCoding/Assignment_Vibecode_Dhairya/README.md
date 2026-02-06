# Groq Chat Streamlit App

A feature-rich Streamlit application that allows you to interact with Groq's API using custom prompts, temperature settings, and advanced conversation management.

## 🚀 Features

### Core Functionality
- **System Prompt Input**: Set the behavior and context for the AI assistant
- **User Prompt Input**: Enter your questions or requests
- **Temperature Control**: Adjust response creativity (0.0 = focused, 2.0 = creative)
- **Environment-based API Key**: Secure API key management through `.env` file

### Advanced Features
- **🧠 Context Retention**: Maintains conversation history for better contextual responses
- **📋 Structured Output Formats**: 7 different response formats for various use cases
- **🔄 Auto-Expand Sidebar**: Automatically shows responses when generated
- **💬 Conversation History**: View and manage previous exchanges
- **🗑️ History Management**: Clear conversation data with one click

### Response Formats
- **📝 General**: Basic structured formatting with headings and bullet points
- **📋 Step-by-Step Guide**: Detailed instructions with prerequisites and tips
- **⚖️ Comparison Analysis**: Detailed comparisons with tables and recommendations
- **💻 Code Solution**: Code solutions with explanations and examples
- **📊 Data Analysis**: Data analysis with insights and visualizations
- **🔧 Troubleshooting Guide**: Problem diagnosis with solutions and prevention
- **📚 Educational Content**: Learning content with objectives and key takeaways

## 🛠️ Setup

### 1. Clone and Install Dependencies
```bash
git clone <repository-url>
cd assign_vibecode
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file and add your Groq API key:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Get a Groq API Key
- Visit [Groq Console](https://console.groq.com/)
- Sign up and create an API key
- Add it to your `.env` file

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Basic Usage
1. **Configure Environment**: Set up your `.env` file with the Groq API key
2. **Set System Prompt**: Define the AI's behavior (optional, defaults to helpful assistant)
3. **Enter User Prompt**: Type your question or request
4. **Adjust Temperature**: Set creativity level (0.0-2.0)
5. **Choose Response Format**: Select the desired output structure
6. **Generate Response**: Click the button to get AI response

### Context Retention
- **Enable/Disable**: Toggle context retention for conversations
- **Automatic Management**: Maintains last 10 exchanges to prevent token overflow
- **Clear History**: Reset conversation data at any time
- **Context Preview**: View recent conversation context before generating

### Response Features
- **Auto-Expand Sidebar**: Responses automatically appear in the sidebar
- **Usage Statistics**: View token usage and response details
- **Conversation History**: Browse previous exchanges in expandable sections
- **Structured Output**: Get well-formatted responses based on selected format

## 🎯 Temperature Guide

- **0.0-0.3**: Very focused, deterministic responses (best for factual answers)
- **0.4-0.7**: Balanced responses (recommended for most use cases)
- **0.8-1.2**: More creative and varied responses
- **1.3-2.0**: Highly creative and unpredictable responses

## 📁 Project Structure

```
assign_vibecode/
├── app.py              # Main Streamlit application
├── prompt.py           # Structured prompt templates and utilities
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore file
└── README.md          # This documentation
```

## 🔧 Technical Details

### Dependencies
- **streamlit==1.28.1**: Web application framework
- **groq==1.0.0**: Groq API client library
- **python-dotenv==1.0.0**: Environment variable management

### Key Components
- **Session State Management**: Handles conversation history and UI state
- **Error Handling**: Comprehensive error messages and recovery
- **Context Building**: Smart conversation history integration
- **Response Formatting**: Multiple structured output templates

### Model Information
- **Default Model**: `llama-3.3-70b-versatile`
- **Max Tokens**: 1024 (configurable)
- **Context Window**: Maintains conversation history efficiently

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your `.env` file contains a valid Groq API key
   - Check that the API key has proper permissions

2. **Import Errors**
   - Run `pip install -r requirements.txt` to install dependencies
   - Ensure you're using Python 3.8+

3. **Context Too Long**
   - The app automatically limits conversation history to 10 exchanges
   - Clear history if you encounter token limit errors

4. **Sidebar Not Expanding**
   - Ensure JavaScript is enabled in your browser
   - Try refreshing the page if the sidebar doesn't auto-expand

### Environment Variables
Create a `.env` file with:
```env
GROQ_API_KEY=your_actual_api_key_here
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your API key and internet connection
3. Review the error messages in the app
4. Ensure all dependencies are properly installed

## 🔄 Updates

Recent improvements include:
- ✅ Context retention for better conversations
- ✅ Auto-expanding sidebar for better UX
- ✅ Multiple structured response formats
- ✅ Environment-based API key management
- ✅ Enhanced error handling and user feedback

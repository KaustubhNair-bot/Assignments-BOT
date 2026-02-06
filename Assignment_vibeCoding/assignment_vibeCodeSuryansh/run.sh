#!/bin/bash

echo "🚀 Starting AI Assistant - Groq Powered..."
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌐 Launching Streamlit app..."
echo "🔗 The app will open in your browser at http://localhost:8501"
streamlit run app.py --server.port 8501 --server.headless false

# 🤖 VibeCode AI Dashboard

A professional, high-end AI Chat Dashboard built with **Streamlit** and powered by **Groq's Llama-3** models. This project demonstrates advanced "Vibe Coding" techniques, modular architecture, and robust prompt engineering to create a seamless user experience.

## 🚀 Key Features

* **Advanced Role-Based Personas**: Choose from specific roles like **Teacher, Coder, Interviewer, Storyteller, or Analyst**. The internal system logic adapts its personality, tone, and formatting based on your choice.
* **Dynamic Model Switching**: Toggle between the high-intelligence `llama-3.3-70b` for complex tasks or the `llama-3.1-8b` for lightning-fast responses.
* **Professional UX/UI**:
    * **Newest-First History**: The latest conversation blocks (User Task + AI Response) appear at the top of the feed, eliminating unnecessary scrolling for new answers.
    * **Modular Dashboard**: A clean 2-column layout with fixed-height scrollable containers for a stable "SaaS-like" feel.
    * **Custom CSS Styling**: Gradient headers, rounded corners, and a professional "Midnight" dark theme.
* **Token Analytics**: Real-time word counting for every AI response to track output length and model efficiency.
* **Invisible Guardrails**: A hidden security layer (`prompt_manager.py`) ensures the AI remains professional and prevents prompt injection or rule leakage.

## 🏗️ Project Architecture

To ensure "Best of the Best" quality, the project follows a **Modular Design Pattern**, separating concerns for better maintainability:

- `main.py`: The orchestrator that manages session state and application flow.
- `src/ui_components.py`: Contains the design logic, layout functions, and custom CSS.
- `src/llm_logic.py`: Handles secure API communication, model parameters, and word counting.
- `src/prompt_manager.py`: The "DNA" of the bot, containing core safety rules and persona definitions.

## 🛠️ Setup & Installation

Follow these steps to run the project on your local machine:

1.  **Clone the Project**:
    Open your terminal and clone the repository to your local machine:
    ```bash
    cd assign_vibeCode
    ```

2.  **Install Dependencies**:
    Run this command to install all required libraries from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment (.env)**:
    * Create a new file named `.env` in the root folder of the project.
    * Paste your Groq API key into the file using the following variable name:
    ```env
    GROQ_API_KEY=your_actual_api_key_here
    ```

4.  **Run the Project**:
    Execute the following command to launch the dashboard in your default web browser:
    ```bash
    streamlit run main.py
    ```
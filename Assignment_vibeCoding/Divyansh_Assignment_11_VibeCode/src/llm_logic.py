import os
from groq import Groq
from dotenv import load_dotenv
from src.prompt_manager import INTERNAL_SYSTEM_PROMPT

load_dotenv()

def get_groq_response(user_task, system_behavior, temp_value, model_selection):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "API Key Missing", 0
    
    client = Groq(api_key=api_key)
    combined_prompt = f"{INTERNAL_SYSTEM_PROMPT}\n\n### USER BEHAVIOR:\n{system_behavior}"

    try:
        response = client.chat.completions.create(
            model=model_selection,
            messages=[{"role": "system", "content": combined_prompt}, {"role": "user", "content": user_task}],
            temperature=temp_value,
        )
        text = response.choices[0].message.content
        return text, len(text.split())
    except Exception as e:
        return f"Error: {str(e)}", 0
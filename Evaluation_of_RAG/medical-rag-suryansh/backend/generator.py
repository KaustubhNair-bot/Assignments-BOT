# This module connects RAG with External LLM
import os
from dotenv import load_dotenv
from groq import Groq
from backend.prompts import SUMMARY_PROMPT, ANSWER_PROMPT

# Load .env
load_dotenv()

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Summarization function
def api_summarize(text):

    prompt = SUMMARY_PROMPT.format(text=text[:2500])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


# Final answer generation function
def generate_answer(query, retrieved_chunks):

    if not retrieved_chunks:
        return "Not enough evidence in hospital records."

    context = "\n\n".join(retrieved_chunks)

    prompt = ANSWER_PROMPT.format(
        context=context,
        query=query
    )

    res = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )

    return res.choices[0].message.content


# Base LLM answer without RAG context (for comparison)
def base_llm_answer(query):

    prompt = f"""
    You are a general medical assistant.

    User Question:
    {query}

    Give a general answer from your knowledge.
    Do not assume access to any patient records.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

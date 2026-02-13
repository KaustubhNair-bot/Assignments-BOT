import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# FIXED temperature inside backend
LLM_TEMPERATURE = 0.2   # factual + strategic balance

def generate_response(query, context_chunks):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context = "\n\n".join([c["text"] for c in context_chunks])

    prompt = f"""
You are a Senior Business Strategy Analyst for McDonald's India.

STRICT INSTRUCTIONS:
- Use ONLY the provided context.
- Do NOT use external knowledge.
- Do NOT summarize all documents.
- Focus only on information directly relevant to the question.
- Integrate financial, competitor, operational, and menu insights when relevant.
- Avoid generic consulting language.
- Keep the response concise (maximum 400 words).
- Base all insights strictly on data present in the context.

CONTEXT:
{context}

QUESTION:
{query}

Provide:

1. Strategic Insight (2–3 sentences)
   - Identify the core business implication supported by the context.

2. Three Strategic Initiatives
   - Concrete, actionable business moves grounded in financial trends, competitor positioning, or product strategy.
   - Each initiative must clearly link to evidence from the context.

3. One Competitive Positioning Move
   - A clear differentiator McDonald's India can leverage based on the data.

4. Two Measurable KPIs
   - Quantifiable metrics directly aligned to the initiatives.

Avoid marketing-heavy language, generic QSR advice, or speculative claims.
Be analytical, data-driven, and practical.
"""


    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=LLM_TEMPERATURE,
        max_tokens=1200
    )

    return response.choices[0].message.content

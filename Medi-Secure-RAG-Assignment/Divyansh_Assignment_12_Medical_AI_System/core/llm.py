import ollama


def generate_medical_summary(query, matching_cases):
    # We give it the doctor's question and the cases we found.

    context_text = ""
    for i, case in enumerate(matching_cases):
        context_text += f"\nCase {i + 1}: {case}\n"

    prompt = f"""
    You are a professional medical assistant. 
    A doctor is asking: "{query}"
    
    I have found the following past cases from our secure database:
    {context_text}
    
    Please provide a very brief, high-level summary of these cases to help the doctor. 
    Focus on common symptoms and treatments mentioned. 
    Keep it professional and concise.
    """

    # Call the local model
    response = ollama.generate(model="gemma3:1b", prompt=prompt)

    return response["response"]

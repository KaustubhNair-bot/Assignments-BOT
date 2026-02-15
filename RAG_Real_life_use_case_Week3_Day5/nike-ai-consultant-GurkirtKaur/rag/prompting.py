"""
Chain-of-Thought Prompting Module for Nike HR RAG Assistant

This module provides structured prompts that enable the LLM to show its reasoning
process explicitly, improving explainability and trust for compliance-critical HR queries.
"""

def get_cot_prompt_template():
    """
    Returns a Chain-of-Thought prompt template that structures the LLM's response
    into 4 clear sections for maximum explainability.
    
    Returns:
        str: Prompt template with placeholders for context and question
    """
    template = """You are a Senior HR Compliance Officer at Nike.

Your task is to answer employee questions about Nike HR policies using ONLY the provided policy context.

IMPORTANT: Structure your response in exactly 4 sections with clear markers:

[THOUGHTS BEFORE RETRIEVAL]
Before looking at the retrieved documents, think aloud about:
- What specific information you need to answer this question
- Which policy areas are likely relevant (leave, conduct, remote work, etc.)
- What key terms or concepts to look for

[SELECTED CHUNKS AND WHY]
List each retrieved document chunk and explain:
- Which policy document it comes from
- Why this chunk is relevant to the question
- What specific information it contains

[REASONING BASED ON CHUNKS]
Step-by-step reasoning:
- How the retrieved information answers the question
- Any conditions, exceptions, or nuances to consider
- Connections between different policy sections if applicable

[FINAL ANSWER]
Provide a concise, professional answer in formal Nike corporate tone:
- Directly answer the employee's question
- Include specific policy details (numbers, dates, requirements)
- If information is not available, state: "This information is not available in the current policy documents."
- Do NOT add external knowledge or assumptions

---

Retrieved Policy Context:
{context}

Employee Question:
{question}

Now provide your structured response:"""
    
    return template


def parse_cot_response(response_text):
    """
    Parses the LLM's structured response into 4 separate sections.
    
    Args:
        response_text: Raw text output from LLM
        
    Returns:
        dict: Contains 'thoughts', 'chunks', 'reasoning', 'answer' keys
    """
    sections = {
        'thoughts': '',
        'chunks': '',
        'reasoning': '',
        'answer': ''
    }
    
    # Define section markers
    markers = {
        'thoughts': '[THOUGHTS BEFORE RETRIEVAL]',
        'chunks': '[SELECTED CHUNKS AND WHY]',
        'reasoning': '[REASONING BASED ON CHUNKS]',
        'answer': '[FINAL ANSWER]'
    }
    
    # Find positions of each marker
    positions = {}
    for key, marker in markers.items():
        pos = response_text.find(marker)
        if pos != -1:
            positions[key] = pos + len(marker)
    
    # Extract content between markers
    if 'thoughts' in positions and 'chunks' in positions:
        sections['thoughts'] = response_text[positions['thoughts']:positions['chunks'] - len(markers['chunks'])].strip()
    
    if 'chunks' in positions and 'reasoning' in positions:
        sections['chunks'] = response_text[positions['chunks']:positions['reasoning'] - len(markers['reasoning'])].strip()
    
    if 'reasoning' in positions and 'answer' in positions:
        sections['reasoning'] = response_text[positions['reasoning']:positions['answer'] - len(markers['answer'])].strip()
    
    if 'answer' in positions:
        sections['answer'] = response_text[positions['answer']:].strip()
    
    # Fallback: if parsing fails, put everything in answer
    if not any(sections.values()):
        sections['answer'] = response_text.strip()
        sections['thoughts'] = "Parsing error - full response shown in Final Answer"
    
    return sections


def format_cot_for_display(cot_sections):
    """
    Formats parsed CoT sections for clean display in Streamlit UI.
    
    Args:
        cot_sections: Dict with 'thoughts', 'chunks', 'reasoning', 'answer' keys
        
    Returns:
        dict: Same structure but with cleaned/formatted text
    """
    formatted = {}
    
    for key, content in cot_sections.items():
        # Remove extra whitespace and newlines
        cleaned = content.strip()
        # Ensure at least some content
        if not cleaned:
            cleaned = f"[No {key} section found in response]"
        formatted[key] = cleaned
    
    return formatted


# Why LLM (70B) over SLM (8B) for Nike HR AI Consultant
WHY_LLM_OVER_SLM = """
## Why We Choose LLM (70B) Over SLM (8B)

For Nike's Internal HR AI Consultant, we exclusively use the **LLM (llama-3.3-70b-versatile)** 
instead of smaller models. Here's why:

### 1. Compliance Requirements
- **HR policy errors have legal consequences**: Incorrect guidance on leave, termination, or 
  conduct violations could expose Nike to legal liability
- **LLM hallucination rate <2%** vs SLM 5-10%: The larger model is significantly more reliable 
  at staying grounded in retrieved context
- **Better uncertainty calibration**: LLM more reliably states "information not available" 
  rather than fabricating plausible-sounding but incorrect details

### 2. Chain-of-Thought Reasoning Quality
- **70B parameters enable deeper reasoning**: Multi-step logical inference required for complex 
  HR policies (e.g., "Can I take parental leave while on a performance improvement plan?")
- **Better instruction following**: More reliably produces structured CoT output with all 4 sections
- **Nuanced understanding**: Handles policy exceptions, edge cases, and conditional requirements 
  that smaller models often miss or oversimplify

### 3. Professional Communication
- **Consistent corporate tone**: LLM maintains formal Nike brand voice across all responses
- **Compliance-focused language**: Uses appropriate legal/HR terminology
- **Adapts to query sensitivity**: Adjusts tone for serious topics (termination, violations) 
  vs routine questions (expense policies)

### 4. Cost-Benefit Analysis
- **LLM cost**: ~$32/month for 10,000 queries
- **SLM cost**: ~$5/month for 10,000 queries
- **Savings**: $27/month
- **Risk**: A single compliance error could cost Nike thousands in legal fees or settlements
- **Verdict**: The $27/month savings is negligible compared to the compliance risk reduction

### 5. Explainability for Audit Trail
- **Chain-of-Thought works best with larger models**: SLMs struggle to maintain reasoning 
  quality while also producing structured output
- **Legal defensibility**: If an employee challenges HR guidance, we can show the complete 
  reasoning chain from policy documents to final answer
- **Trust building**: Employees see the "thinking process" and understand how answers are derived

### 6. Groq's Speed Advantage
- **LLM response time**: 2-4 seconds (acceptable for HR queries)
- **SLM response time**: 0.5-1 second (faster but not critical for this use case)
- **Groq's LPU inference**: Makes even 70B models fast enough for production
- **User experience**: Employees are willing to wait 2-3 seconds for accurate HR guidance

### Conclusion
For compliance-critical applications like HR policy assistance, **accuracy and explainability 
trump speed and cost**. The LLM's superior reasoning, lower hallucination rate, and better 
Chain-of-Thought capabilities make it the only responsible choice for Nike's HR Assistant.
"""

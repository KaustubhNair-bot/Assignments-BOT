import faiss
import pickle
import os
import re
import json
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder
from groq import Groq

# load API
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# load FAISS index
index = faiss.read_index("faiss_index/index.faiss")

with open("faiss_index/chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# embedding model & reranker
model = SentenceTransformer("BAAI/bge-base-en-v1.5")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# conversation memory storage
class ConversationMemory:
    """Stores conversation history for context-aware responses"""
    
    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns
    
    def add_turn(self, user_query, assistant_response):
        """Add a conversation turn"""
        self.history.append({
            "user": user_query,
            "assistant": assistant_response
        })
        
        # keep only last N turns
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]
    
    def get_context(self):
        """Format conversation history as context"""
        if not self.history:
            return ""
        
        context = "Previous conversation:\n"
        for i, turn in enumerate(self.history, 1):
            context += f"User: {turn['user']}\n"
            context += f"Assistant: {turn['assistant']}\n\n"
        
        return context
    
    def get_last_n_queries(self, n=3):
        """Get last N user queries for query rewriting"""
        return [turn["user"] for turn in self.history[-n:]]
    
    def clear(self):
        """Clear conversation history"""
        self.history = []


# confidence label
def confidence_label(score):
    if score > 0.75:
        return "High Confidence"
    elif score > 0.55:
        return "Medium Confidence"
    else:
        return "Low Confidence"


# query rewriting
def rewrite_query(original_query, conversation_history):
    """
    Rewrite query with conversation context for better retrieval.
    Resolves pronouns, adds missing context, expands abbreviations.
    """
    
    if not conversation_history:
        return original_query
    
    recent_queries = conversation_history[-3:]  # last 3 turns
    
    # build context string
    context = "Recent conversation:\n"
    for turn in recent_queries:
        context += f"User: {turn['user']}\n"
        context += f"Assistant: {turn['assistant'][:100]}...\n"
    
    prompt = f"""Given this conversation context, rewrite the user's latest query to be standalone and clear for semantic search.

{context}

Latest query: "{original_query}"

Rules:
1. Resolve pronouns (it, this, that) to specific entities
2. Add missing context from conversation
3. Expand abbreviations (PS5, HDMI, etc.)
4. Keep it concise (max 2 sentences)
5. If query is already clear, return it unchanged

Rewritten query:"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70B-versatile",
            messages=[
                {"role": "system", "content": "You are a query rewriting assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        rewritten = completion.choices[0].message.content.strip()
        
        # fallback if rewriting fails
        if len(rewritten) < 5 or len(rewritten) > 200:
            return original_query
        
        return rewritten
    
    except Exception as e:
        print(f"Query rewriting failed: {e}")
        return original_query


# hybrid retrieval + reranking
def retrieve_and_rerank(query, k=20, top_n=5):
    """
    Two-stage retrieval:
    1. FAISS semantic search (k=20)
    2. Cross-encoder reranking (top_n=5)
    """
    
    # stage 1: FAISS retrieval 
    query_vector = model.encode([query], normalize_embeddings=True)
    query_vector = np.array(query_vector)
    
    D, I = index.search(query_vector, k)
    
    retrieved_chunks = [chunks[i] for i in I[0]]
    semantic_scores = D[0]
    
    # keyword boost 
    keyword_scores = []
    for chunk in retrieved_chunks:
        match_count = sum(
            1 for word in query.lower().split()
            if word in chunk.lower()
        )
        keyword_scores.append(match_count * 0.03)
    
    initial_scores = semantic_scores + np.array(keyword_scores)
    
    # stage 2: reranking with cross-encoder
    pairs = [[query, chunk] for chunk in retrieved_chunks]
    rerank_scores = reranker.predict(pairs)
    
    # combine scores (60% reranker, 40% initial)
    final_scores = 0.6 * np.array(rerank_scores) + 0.4 * initial_scores
    
    # sort by combined score
    sorted_indices = np.argsort(final_scores)[::-1]
    
    # return top N
    top_chunks = [retrieved_chunks[i] for i in sorted_indices[:top_n]]
    top_scores = [final_scores[i] for i in sorted_indices[:top_n]]
    
    return top_chunks, top_scores



# structured output extraction
def extract_structured_data(query, answer):
    
    structured_data = {
        "error_codes": [],
        "model_numbers": [],
        "part_numbers": [],
        "specifications": {}
    }
    
    # extract error codes 
    error_pattern = r'\b[A-Z]{2}-\d{6}-\d\b'
    structured_data["error_codes"] = re.findall(error_pattern, answer)
    
    # extract model numbers 
    model_pattern = r'\b(?:CFI|PS5|CUH)-[\w\d-]+\b'
    structured_data["model_numbers"] = re.findall(model_pattern, answer)
    
    # extract part numbers 
    part_pattern = r'\b(?:M\.2\s+\d{4}|PCIe\s+\d\.\d|Gen\s*\d)\b'
    structured_data["part_numbers"] = re.findall(part_pattern, answer)
    
    # extract specifications 
    specs_patterns = {
        "storage": r'(\d+(?:\.\d+)?)\s*(GB|TB|terabytes?|gigabytes?)',
        "speed": r'(\d+(?:\.\d+)?)\s*(Gbps|MB/s|mbps)',
        "dimensions": r'(\d+)\s*x\s*(\d+)\s*(?:x\s*(\d+))?\s*(?:mm|cm)',
        "power": r'(\d+)\s*(?:W|watts?|volts?|V)',
    }
    
    for spec_type, pattern in specs_patterns.items():
        matches = re.findall(pattern, answer, re.IGNORECASE)
        if matches:
            structured_data["specifications"][spec_type] = matches
    
    # clean up empty fields
    structured_data = {k: v for k, v in structured_data.items() if v}
    
    return structured_data if structured_data else None


# conversational answer generation WITH TRUE CHAIN-OF-THOUGHT
def generate_answer_with_memory(
    query, 
    retrieved_chunks, 
    retrieval_scores,
    conversation_memory,
    temperature=0.3, 
    show_cot=False
):
    """Generate answer with conversation context and optional CoT reasoning"""
    
    context = "\n\n".join(retrieved_chunks)
    conversation_context = conversation_memory.get_context()
    
    system_prompt = """
You are a professional and Senior PlayStation Support Specialist.

Guidelines:
1. Use ONLY the information available in the provided context.
2. Consider the conversation history to provide contextual responses.
3. If the user refers to something from earlier ("it", "that issue"), use conversation history,but dont mention it explictly but mildly.
4. For follow-up questions, build upon previous answers.
5. Maintain a polite and helpful tone.
6. Do not invent information beyond the context.
7. For technical specs, be precise with model numbers, error codes, and part numbers.
"""

    # CRITICAL CHANGE: True Chain-of-Thought for retrieval logic
    if show_cot:
        # Build retrieval metadata for the model to reason about
        retrieval_info = "\n".join([
            f"Chunk {i+1} (Relevance Score: {retrieval_scores[i]:.3f}):\n{chunk[:150]}..."
            for i, chunk in enumerate(retrieved_chunks)
        ])
        
        cot_instruction = f"""
CRITICAL: You MUST explain your retrieval and reasoning process BEFORE providing the answer.

Available Retrieved Information:
{retrieval_info}

Use this EXACT format:

**🔍 RETRIEVAL REASONING:**

**Query Analysis:** 
[Explain what the user is specifically asking for and any technical terms involved]

**Source Selection & Relevance:**
[For each relevant chunk, explain:
 - Which chunk(s) you're using (mention by number and score)
 - Why each chunk is relevant to answering this query
 - What specific information each provides]

**Confidence Assessment:**
[Based on the retrieval scores and content quality:
 - How confident are you in this answer (High/Medium/Low)?
 - Are there any gaps in the retrieved information?
 - Is the information sufficient and authoritative?]

**Information Synthesis:**
[If using multiple chunks, explain how you're combining them.
 If conversation history is relevant, mention how it helps interpret the query.]

---

**💡 FINAL ANSWER:**
[Now provide your actual support response using the retrieved information]

Remember: The user can see the retrieved chunks separately, so your reasoning should explain WHY and HOW you're using them, not just repeat them.
"""
    else:
        cot_instruction = """
Respond in a polite and helpful tone.
Consider conversation history for context.
Use bullet points for troubleshooting steps.
Highlight important technical terms in **bold**.
Include specific model numbers, error codes, or part numbers when relevant.
Provide clear, actionable guidance based on the retrieved context.
"""

    user_prompt = f"""
{conversation_context}

Current Question:
{query}

Retrieved Context:
{context}

Instructions:
{cot_instruction}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70B-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        top_p=0.9,
        max_tokens=800 if show_cot else 600  # More tokens for CoT reasoning
    )

    return completion.choices[0].message.content


# injecting official links 
def inject_official_links(answer, retrieved_chunks, structured_data):
    """Enhanced link injection with structured data awareness"""
    
    official_links = {
        "dualsense": "https://www.playstation.com/support/hardware/dualsense-controller/",
        "safe mode": "https://www.playstation.com/support/hardware/safe-mode-playstation/",
        "hdmi": "https://www.playstation.com/support/hardware/ps5/",
        "video": "https://www.playstation.com/support/hardware/ps5/",
        "network": "https://www.playstation.com/support/connectivity/",
        "storage": "https://www.playstation.com/support/hardware/ps5-install-m2-ssd/",
        "error": "https://www.playstation.com/support/error-codes/",
    }
    
    combined_text = " ".join(retrieved_chunks).lower()
    
    # add error code specific link if error codes detected
    if structured_data and "error_codes" in structured_data:
        answer += f"\n\n**Detected Error Code(s):** {', '.join(structured_data['error_codes'])}"
        answer += f"\n🔗 Error Code Reference: {official_links['error']}"
        return answer
    
    # add general support link
    for keyword, link in official_links.items():
        if keyword in combined_text:
            answer += f"\n\n🔗 For additional guidance, visit:\n{link}"
            break
    
    return answer


# RAG pipeline
def rag_pipeline_enhanced(
    query, 
    conversation_memory,
    temperature=0.3, 
    show_cot=False,
    enable_rewriting=True,
    enable_reranking=True
):
    # query rewriting (if enabled and history exists)
    original_query = query
    if enable_rewriting and conversation_memory.history:
        query = rewrite_query(query, conversation_memory.history)
        query_modified = (query != original_query)
    else:
        query_modified = False
    
    # retrieval and reranking
    if enable_reranking:
        retrieved, scores = retrieve_and_rerank(query, k=20, top_n=5)
    else:
        # fallback to original retrieval
        retrieved, scores = retrieve_original(query)
    
    top_score = float(scores[0])
    label = confidence_label(top_score)
    
    # soft fallback logic
    if top_score < 0.45:
        answer = (
            "I couldn't find specific guidance for that issue in the official knowledge base. "
            "However, here is some related information that may help:"
        )
    else:
        # CRITICAL: Pass scores to generation function for CoT reasoning
        answer = generate_answer_with_memory(
            original_query,
            retrieved,
            scores,  # NEW: Passing scores for CoT analysis
            conversation_memory,
            temperature, 
            show_cot
        )
    
    structured_data = extract_structured_data(original_query + " " + answer, answer)
    
    answer = inject_official_links(answer, retrieved, structured_data)
    
    conversation_memory.add_turn(original_query, answer)
    
    return {
        "answer": answer,
        "retrieved_chunks": retrieved,
        "scores": scores,
        "confidence_label": label,
        "structured_data": structured_data,
        "query_rewritten": query_modified,
        "rewritten_query": query if query_modified else None
    }

# original retrieval (for backward compatibility)
def retrieve_original(query, k=8):
    """Original retrieval without reranking"""
    query_vector = model.encode([query], normalize_embeddings=True)
    query_vector = np.array(query_vector)
    
    D, I = index.search(query_vector, k)
    
    retrieved_chunks = [chunks[i] for i in I[0]]
    semantic_scores = D[0]
    
    # keyword boost
    keyword_scores = []
    for chunk in retrieved_chunks:
        match_count = sum(
            1 for word in query.lower().split()
            if word in chunk.lower()
        )
        keyword_scores.append(match_count * 0.03)
    
    final_scores = semantic_scores + np.array(keyword_scores)
    
    return retrieved_chunks, final_scores


# backward compatible function
def rag_pipeline(query, temperature=0.3, show_cot=False):
    """
    Backward compatible wrapper for existing code.
    Uses enhanced pipeline without conversation memory.
    """
    temp_memory = ConversationMemory(max_turns=1)
    
    result = rag_pipeline_enhanced(
        query,
        temp_memory,
        temperature,
        show_cot,
        enable_rewriting=False,
        enable_reranking=True
    )
    
    return (
        result["answer"],
        result["retrieved_chunks"],
        result["scores"],
        result["confidence_label"]
    )

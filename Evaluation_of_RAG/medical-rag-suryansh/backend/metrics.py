import re
from collections import Counter

# ---------- TEXT HELPERS ----------

def tokenize(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return t.split()


# ---------- METRICS ----------

def keyword_coverage(answer, query):

    medical_terms = {
        "cough": ["cough","sputum","infection","bronchitis","viral","bacterial"],
        "pneumonia": ["antibiotic","fever","xray","crp","iv","oxygen"],
        "asthma": ["wheezing","bronchodilator","albuterol","peak","steroid"],
        "copd": ["smoking","bronchodilator","steroid","oxygen","spirometry"],
        "chest pain": ["angina","ecg","troponin","ischemia","mi"]
    }

    key = None
    for k in medical_terms:
        if k in query.lower():
            key = k

    if not key:
        return 0

    words = tokenize(answer)
    hits = sum(1 for w in medical_terms[key] if w in words)

    return round((hits / len(medical_terms[key])) * 100, 2)


def faithfulness(answer, retrieved):

    context = " ".join(retrieved).lower()
    a = tokenize(answer)

    if not a:
        return 0

    supported = sum(1 for w in a if w in context)

    return round((supported / len(a)) * 100, 2)


def hallucination_proxy(answer, retrieved):

    context = " ".join(retrieved).lower()
    a = tokenize(answer)

    hallucinated = sum(1 for w in a if w not in context)

    return round((hallucinated / max(len(a),1)) * 100, 2)


def clinical_utility(answer):

    score = 0
    a = answer.lower()

    if any(w in a for w in ["diagnosis","suggest","likely"]):
        score += 1

    if any(w in a for w in ["treat","management","antibiotic","therapy"]):
        score += 1

    if any(w in a for w in ["red flag","emergency","warning"]):
        score += 1

    if any(w in a for w in ["source","record","case"]):
        score += 1

    levels = {
        4: "Excellent",
        3: "Good",
        2: "Adequate",
        1: "Weak",
        0: "Poor"
    }

    return levels[score]


def evaluate_pair(query, base, rag, context):

    return {
        "base_keyword_cov": keyword_coverage(base, query),
        "rag_keyword_cov": keyword_coverage(rag, query),

        "rag_faithfulness": faithfulness(rag, context),
        "rag_hallucination": hallucination_proxy(rag, context),

        "base_len": len(base.split()),
        "rag_len": len(rag.split()),

        "rag_clinical_utility": clinical_utility(rag),
        "base_clinical_utility": clinical_utility(base)
    }

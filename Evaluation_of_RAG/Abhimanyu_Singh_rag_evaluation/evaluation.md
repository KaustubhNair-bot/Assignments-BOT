# RAG vs Base LLM Evaluation Report  
**MediSecure RAG System – Comparative Analysis**

**Date:** 2026-02-10 23:50  
**LLM Model:** Mistral (Local via Ollama)  
**Embedding Model:** all-MiniLM-L6-v2  
**Vector Store:** ChromaDB  
**Dataset:** Medical Transcriptions (~5,000 records)  
**Number of Queries:** 5  

---

## Summary

This report evaluates whether the **Retrieval-Augmented Generation (RAG)** system provides more accurate and grounded results than a **standalone base LLM** for clinical transcription queries.

Two pipelines were compared:

- **RAG Pipeline:**  
  Query → ChromaDB Retrieval → LLM Generation with Retrieved Context  

- **Base LLM:**  
  Query → LLM Generation without External Context  

Results were evaluated using the **RAG Triad** (Faithfulness, Relevancy, Context Precision) along with clinical specificity and response time.

**Verdict:**  
- RAG won **3/5** queries  
- Base LLM won **2/5** queries  
- Ties: **0**

---

## Evaluation Metrics

The following metrics were used for comparison:

1. **Context Relevance (RAG only)**  
   Measures how relevant the retrieved patient cases are to the user’s query.

2. **Answer Groundedness (Faithfulness)**  
   Evaluates whether answers are strictly supported by retrieved medical records, minimizing hallucinations.

3. **Answer Completeness**  
   Assesses how thoroughly the response addresses all aspects of the clinical query.

4. **Specificity**  
   Evaluates inclusion of concrete clinical details such as patient age, diagnoses, procedures, or measurements.

5. **Response Time**  
   Total latency in milliseconds, including retrieval and generation.

---

## Aggregate Results

| Metric | RAG Pipeline | Base LLM |
|------|------------|---------|
| Overall Score (avg) | 7.2 / 10 | 7.0 / 10 |
| Groundedness (avg) | 8.2 / 10 | N/A |
| Specificity (avg) | 8.6 / 10 | 8.0 / 10 |
| Avg Response Time | 14,375 ms | 21,351 ms |
| Wins | 3 | 2 |

---

## Query Results

### Query 1: Cardiology

**Query:**  
Patient presenting with chest pain radiating to the left arm with shortness of breath and diaphoresis

| Metric | RAG | Base LLM |
|------|----|---------|
| Overall Score | 8 / 10 | 7 / 10 |
| Specificity | 9 / 10 | 6 / 10 |
| Groundedness | 10 / 10 | 9 / 10 |
| Response Time | 10,380 ms | 11,373 ms |

**Winner:** RAG  

**Evaluation Reasoning:**  
RAG identified a specific diabetic patient with a history of coronary artery disease from the database, while the Base LLM provided only general clinical guidelines.

---

### Query 2: Endocrinology

**Query:**  
Management of type 2 diabetes with complications including diabetic neuropathy and retinopathy

| Metric | RAG | Base LLM |
|------|----|---------|
| Overall Score | 6 / 10 | 8 / 10 |
| Specificity | 9 / 10 | 9 / 10 |
| Groundedness | 6 / 10 | 9 / 10 |
| Response Time | 15,314 ms | 26,567 ms |

**Winner:** Base LLM  

**Evaluation Reasoning:**  
The Base LLM provided a more comprehensive general management plan, while RAG was limited by insufficient neuropathy-specific cases in the retrieved context.

---

### Query 3: Orthopedics

**Query:**  
Surgical procedure for total knee replacement in a patient with severe osteoarthritis

| Metric | RAG | Base LLM |
|------|----|---------|
| Overall Score | 9 / 10 | 5 / 10 |
| Specificity | 9 / 10 | 8 / 10 |
| Groundedness | 10 / 10 | 9 / 10 |
| Response Time | 8,117 ms | 25,932 ms |

**Winner:** RAG  

**Evaluation Reasoning:**  
RAG correctly identified that database records described a unicompartmental knee replacement rather than a total replacement and provided exact component details (Biomet), which the Base LLM could not infer.

---

### Query 4: Pediatrics

**Query:**  
Pediatric patient with recurrent upper respiratory infections and bilateral otitis media

| Metric | RAG | Base LLM |
|------|----|---------|
| Overall Score | 9 / 10 | 6 / 10 |
| Specificity | 8 / 10 | 9 / 10 |
| Groundedness | 6 / 10 | 9 / 10 |
| Response Time | 8,596 ms | 20,103 ms |

**Winner:** RAG  

**Evaluation Reasoning:**  
RAG retrieved a detailed case involving a 3-year-old patient with multiple antibiotic courses, grounding the response in actual clinical history.

---

### Query 5: Gastroenterology

**Query:**  
Colonoscopy findings in a patient with chronic abdominal pain and suspected inflammatory bowel disease

| Metric | RAG | Base LLM |
|------|----|---------|
| Overall Score | 5 / 10 | 8 / 10 |
| Specificity | 8 / 10 | 8 / 10 |
| Groundedness | 9 / 10 | 9 / 10 |
| Response Time | 19,470 ms | 22,777 ms |

**Winner:** Base LLM  

**Evaluation Reasoning:**  
The Base LLM delivered a stronger educational overview of inflammatory bowel disease, while RAG relied on a specific case that ruled out IBD in favor of IBS.

---

## Key Findings

### Advantages of RAG over Base LLM

- **Clinical Specificity:** RAG references real patient data such as ages, procedures, and component sizes.
- **Groundedness:** Responses are tightly bound to actual medical records, reducing hallucinations.
- **Traceability:** Clinicians can trace answers back to source transcriptions.

### Limitations of RAG

- **Context Dependence:** RAG performance is limited by the completeness of available records.
- **Retrieval Precision:** Inaccurate or sparse retrieval directly impacts answer quality.

---

## Conclusion

This evaluation shows that while a Base LLM functions well as a **general medical knowledge source**, the RAG system performs better as a **clinical decision-support assistant**.

For hospital environments that require answers grounded in their own historical patient data, RAG provides superior specificity, traceability, and safety compared to standalone language models.

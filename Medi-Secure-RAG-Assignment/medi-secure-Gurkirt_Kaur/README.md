# Medi-Secure - Hospital RAG System

A simple medical search system for private hospitals. Doctors can search for similar patient cases using natural language from the existing medical transcription database.

## What It Does
- Secure login for doctors and administrators
- Search patient notes using natural language (like "chest pain" or "diabetes symptoms")
- Uses `mtsamples.csv` as the knowledge base (no file uploads needed)
- Keeps all patient data secure and private
- Semantic search using vector embeddings

## Architecture
- **Backend API** (FastAPI): Handles authentication and search
- **Frontend** (Streamlit): Simple web interface
- **Knowledge Base**: Uses `mtsamples.csv` dataset with 5,000+ medical transcriptions

## How to Install and Run

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start the API server:**
```bash
cd app
python main.py
```

4. **Start the frontend:**
```bash
cd frontend
streamlit run app.py
```

5. **Open your browser** and go to `http://localhost:8501`  

## Login Credentials
- **Doctor**: username `doctor`, password `doctor123`
- **Admin**: username `admin`, password `admin123`

## Embeddings and Vector Data

This project uses locally generated embeddings for semantic search.

   - Embeddings are not included in the GitHub repository
   - They are generated from mtsamples.csv on first run (or via a setup script)
   - This mirrors real-world RAG system design, where embeddings are derived data

Why embeddings are not tracked:

   - They can be regenerated at any time  
   - They can be large binary files
   - They may encode sensitive medical information
   - Keeping them untracked keeps the repository clean and secure

If embeddings are missing, the backend will prompt the user to generate them.

## API Endpoints

### 1. POST `/login`
JWT authentication endpoint
```json
{
  "username": "doctor",
  "password": "doctor123"
}
```
Returns:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": "doctor"
}
```

### 2. POST `/search`
Search medical transcriptions (requires JWT token)
```json
{
  "query": "chest pain and shortness of breath",
  "limit": 5
}
```
Headers: `Authorization: Bearer <token>`

### 3. GET `/stats`
Get system statistics (requires JWT token)
Headers: `Authorization: Bearer <token>`

## How to Use

1. **Login** with your credentials
2. **Search** for medical conditions or symptoms
3. **View** similar patient cases with:
   - Similarity scores
   - Medical specialty
   - Description
   - Full transcription text
4. **Statistics** shows total cases and specialties

## File Structure
```
medi-secure/
├── app/
│   ├── main.py              # FastAPI backend 
│   └── config.py            # Simple configuration
├── frontend/
│   └── app.py               # Streamlit frontend
├── data/
│   └── mtsamples.csv        # Medical transcriptions (knowledge base)
├── embeddings/              # Generated locally (gitignored)
├── requirements.txt         # Main dependencies
└── README.md             
```

## Security Considerations
- All data remains on the local system
- No external APIs are used
- Authentication via JWT tokens
- Passwords are hashed
- No file uploads or data persistence beyond local storage
- Designed with healthcare data privacy in mind

## Technical Details
- **Knowledge Base**: 5,000+ medical transcriptions from `mtsamples.csv`
- **Search**: Embedding-based semantic search with similarity scoring
- **API**: FastAPI with 3 simple endpoints
- **Frontend**: Streamlit web interface
- **Authentication**: JWT tokens with 30-minute expiration


## Tech Stack Justification

**FastAPI (Backend)**
FastAPI was chosen for the backend because it is lightweight, fast, and easy to work with. It makes it simple to create REST APIs and handle authentication, which was important for managing secure access for doctors and administrators. Its clear structure also helped keep the backend code organized and readable.

**Streamlit (Frontend)**
Streamlit was selected for the frontend because it allows building interactive web applications using only Python code. This made it easy to create a user-friendly interface without needing to learn HTML, CSS, or JavaScript. It also integrates well with data analysis libraries like Pandas, which was useful for displaying medical search results.

**Pandas (Data)**
Pandas was used to load and process the medical transcription dataset stored in CSV format. It provides simple, table-like data structures that make filtering, searching, and handling large amounts of structured medical text efficient and easy to understand.

**JWT (Security)**
JWT was chosen for authentication because it is an industry standard that provides secure token-based login system. It allows for stateless authentication, which is perfect for this application since it doesn't require a database for storing session information.

**Python (Language)**
Python was selected as the primary language because it is the most popular programming language with a huge community and extensive learning resources. Its simplicity and readability made it ideal for building a medical information system that is both functional and easy to understand.

## What I Learned During This Assignment

- During this assignment, I learned how different components of a real-world information retrieval system work together. I gained hands-on experience building a complete pipeline that connects a backend API, a frontend interface, and a data source.

- I learned how semantic search works using embeddings and why it is more effective than basic keyword matching, especially for medical text where the same condition can be described in many ways. This helped me better understand the practical use of Retrieval-Augmented Generation (RAG) concepts.

- I also learned how to design and secure a REST API using FastAPI, including handling authentication and protecting endpoints. Connecting the API to a Streamlit frontend showed me how frontend and backend systems communicate in practice.

Finally, the assignment helped me understand the importance of data privacy, security, and good project structure. Decisions such as keeping embeddings untracked and running everything locally reinforced best practices that are especially important when working with sensitive healthcare data.

# API Reference

## DP World RAG Chatbot — API Documentation

Base URL: `http://localhost:8000`  
Interactive Docs: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 🔵 Health Endpoints

### GET `/api/v1/health/`
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 1234.56
}
```

### GET `/api/v1/health/detailed`
Detailed health check with service statuses.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "redis": "healthy",
    "groq": "configured",
    "cohere": "configured",
    "pinecone": "configured"
  },
  "uptime_seconds": 1234.56
}
```

### GET `/api/v1/health/metrics`
Application metrics (counters, timers).

---

## 💬 Chat Endpoints

### POST `/api/v1/chat/`
Send a message and receive a RAG-powered response.

**Request:**
```json
{
  "message": "What services does DP World offer?",
  "session_id": "optional-session-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "response": "DP World offers...",
    "sources": ["https://dpworld.com/services"],
    "session_id": "uuid"
  }
}
```

### POST `/api/v1/chat/session`
Create a new chat session.

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "message": "Welcome message..."
  }
}
```

### GET `/api/v1/chat/history/{session_id}`
Get chat history for a session.

### DELETE `/api/v1/chat/session/{session_id}`
Delete a session and its history.

---

## 📝 Feedback Endpoints

### POST `/api/v1/feedback/`
Submit feedback on a response.

**Request:**
```json
{
  "session_id": "uuid",
  "rating": 5,
  "comment": "Very helpful!",
  "message_id": "uuid"
}
```

### GET `/api/v1/feedback/stats`
Get aggregate feedback statistics.

---

## 🔧 Admin Endpoints

### GET `/api/v1/admin/stats`
System stats including Pinecone index info and metrics.

### POST `/api/v1/admin/reindex`
Trigger background re-ingestion pipeline.

### POST `/api/v1/admin/clear-index`
Clear all vectors in Pinecone.

### GET `/api/v1/admin/metrics/reset`
Reset application metrics.

---

## Error Responses

All errors follow a standard format:

```json
{
  "success": false,
  "error": "Error Type",
  "detail": "Human-readable description",
  "status_code": 422
}
```

| Code | Description              |
|------|--------------------------|
| 400  | Bad Request              |
| 404  | Not Found                |
| 422  | Validation Error         |
| 429  | Rate Limit Exceeded      |
| 500  | Internal Server Error    |

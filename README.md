# URL Shortener Service

A simple, fast, and reliable URL shortening service built with Flask, similar to bit.ly or tinyurl.

---

## 🚀 Features

✅ **URL Shortening:** Convert long URLs into 6-character alphanumeric short codes
✅ **Redirection:** Fast redirects from short codes to original URLs
✅ **Analytics:** Track click counts and creation timestamps
✅ **Thread-Safe:** Handles concurrent requests properly
✅ **Input Validation:** Robust URL validation and normalization
✅ **Error Handling:** Comprehensive error handling with proper HTTP status codes

---

## 📋 Prerequisites for the project

* Python 3.8 or higher
* `pip` (Python package installer)

---

## 🛠️ Installation & Setup

**Clone/Download the repository**

```bash
git clone <repository-url>
cd url-shortener
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Start the application**

```bash
python -m flask --app app.main run
```

**Verify installation**
The API will be available at [http://localhost:5000](http://localhost:5000)

**Test with:**

```bash
curl http://localhost:5000/
```

---

## 🧪 Running Tests

**Run the complete test suite:**

```bash
pytest
```

**Run tests with verbose output:**

```bash
pytest -v
```

**Run specific test file:**

```bash
pytest test_basic.py
```

---

## 📁 Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py          # Flask application and API endpoints
│   ├── models.py        # Data models and storage
│   └── utils.py         # Utility functions
├── test.py              # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── NOTES.md             # Implementation notes
└── README.md            # This file
```

---

## 🔌 API Endpoints

### 1. Health Check

**GET /**

```bash
curl http://localhost:5000/
```

Response:

```json
{
  "status": "healthy",
  "service": "URL Shortener API"
}
```

---

### 2. API Health Check

**GET /api/health**

```bash
curl http://localhost:5000/api/health
```

Response:

```json
{
  "status": "ok",
  "message": "URL Shortener API is running"
}
```

---

### 3. Shorten URL

**POST /api/shorten**

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

Response:

```json
{
  "short_code": "abc123",
  "short_url": "http://localhost:5000/abc123"
}
```

**Supported URL formats:**

* [https://example.com](https://example.com)
* [http://example.com](http://example.com)
* example.com (auto-normalized to [https://example.com](https://example.com))

---

### 4. Redirect to Original URL

**GET /\<short\_code>**

```bash
curl -L http://localhost:5000/abc123
```

Response: **HTTP 302 redirect to the original URL**

---

### 5. Get Analytics

**GET /api/stats/\<short\_code>**

```bash
curl http://localhost:5000/api/stats/abc123
```

Response:

```json
{
  "url": "https://www.example.com/very/long/url",
  "short_code": "abc123",
  "clicks": 5,
  "created_at": "2024-01-01T10:00:00.123456"
}
```

---

## 📊 Usage Examples

**Complete Workflow Example**

```bash
# 1. Shorten a URL
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.github.com/user/repository"}'

# Response: {"short_code": "gh7x2k", "short_url": "http://localhost:5000/gh7x2k"}

# 2. Use the short URL (redirect and increment click count)
curl -L http://localhost:5000/gh7x2k

# 3. Check analytics
curl http://localhost:5000/api/stats/gh7x2k
# Response: {"url": "https://www.github.com/user/repository", "clicks": 1, "created_at": "2024-01-01T10:00:00.123456"}

# 4. Use the short URL a few more times
curl -L http://localhost:5000/gh7x2k
curl -L http://localhost:5000/gh7x2k

# 5. Check updated analytics
curl http://localhost:5000/api/stats/gh7x2k
# Response: {"url": "https://www.github.com/user/repository", "clicks": 3, "created_at": "2024-01-01T10:00:00.123456"}
```

---

## ⚠️ Error Handling

The API returns appropriate HTTP status codes and error messages:

**400 Bad Request**

```json
{
  "error": "Invalid URL format"
}
```

**404 Not Found**

```json
{
  "error": "Short code not found"
}
```

**500 Internal Server Error**

```json
{
  "error": "Internal server error"
}
```

---

## 🏗️ Architecture

**Components**

* **Flask Application (app/main.py)**
  RESTful API endpoints, request validation, error handling, HTTP response management

* **Data Models (app/models.py)**
  `URLMapping`: Stores URL data and analytics
  `URLStore`: Thread-safe in-memory storage

* **Utilities (app/utils.py)**
  URL validation, normalization, short code generation, helper functions

**Key Features**

* Thread Safety: Uses `threading.RLock()` for concurrent request handling
* Input Validation: Robust URL validation with multiple checks
* Error Handling: Comprehensive error handling at all levels
* Clean Architecture: Separation of concerns with modular design

---

## 🧪 Testing

The test suite includes 20+ comprehensive tests covering:

✅ **Core Functionality**

* URL shortening
* URL redirection
* Analytics tracking

✅ **Error Cases**

* Invalid URLs
* Missing parameters
* Non-existent short codes

✅ **Edge Cases**

* Empty inputs
* Malformed requests
* URL normalization

✅ **Concurrency**

* Thread-safe operations
* Concurrent click counting

**Test Categories**

```bash
pytest -k "test_shorten"     # URL shortening tests
pytest -k "test_redirect"    # Redirection tests
pytest -k "test_stats"       # Analytics tests
pytest -k "test_concurrent"  # Concurrency tests
```

# LLM Automated Database Query Engine

An end-to-end system to query real-time MongoDB transactions using natural language powered by LLMs. Convert plain English questions into safe, read-only MongoDB queries automatically.

## 📋 Overview

**LLMAutomatedDB** is a production-grade application that bridges the gap between natural language and database queries. Users can ask questions in plain English (e.g., "Show all failed transactions from today"), and the system automatically generates and executes safe MongoDB queries without requiring SQL/MongoDB knowledge.

The system uses LLMs (via Groq API) to intelligently translate user intent into MongoDB queries while maintaining strict safety constraints to prevent unauthorized data access or destructive operations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (React + Vite + TS)               │
│              (Port 5173 - Web Console)                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Request
                     │ (Natural Language Query)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                      │
│              (Port 8000 - REST API)                     │
│  ┌───────────────────────────────────────────────────┐ │
│  │ LLM Engine (Groq - Llama 3.1 8B Instant)         │ │
│  │ • Processes natural language                      │ │
│  │ • Generates MongoDB queries                       │ │
│  │ • Enforces safety constraints                     │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Query Validator                                   │ │
│  │ • Validates query structure                       │ │
│  │ • Prevents unsafe operations                      │ │
│  │ • Enforces read-only access                       │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ MongoDB Query
                     │ (Authenticated)
                     ▼
┌─────────────────────────────────────────────────────────┐
│           MongoDB Database                              │
│       (payments.transactions collection)                │
│      • 500+ sample transactions                         │
│      • Optimized indexes                               │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** (0.110.0) - Modern async web framework
- **Uvicorn** (0.27.1) - ASGI web server
- **PyMongo** (4.6.1) - MongoDB driver
- **Groq API** (0.9.0) - LLM provider (Llama 3.1 8B Instant)
- **Pydantic** (2.6.1) - Data validation
- **Python-dotenv** (1.0.1) - Environment configuration
- **HTTPX** (0.26.0) - Async HTTP client
- **Pytest** (7.4.0) - Testing framework

### Frontend
- **React** (19.2) - Modern UI library
- **Vite** (8.0) - Frontend build tool and development server
- **TypeScript** - Strong type-safety and static validation
- **TailwindCSS** (4.0) - Styling framework
- **Zustand** & **TanStack Query** - Robust application state management

### Infrastructure
- **MongoDB** - Document-oriented NoSQL database
- **Docker & Docker Compose** - Containerization & orchestration

### Core Dependencies
- **Python 3.9+**
- **MongoDB Atlas** or local MongoDB instance

## ✨ Features

✅ **Natural Language Processing** - Ask database questions in plain English
✅ **Safe Query Generation** - LLM-powered MongoDB query generation with safety constraints
✅ **Read-Only Access** - Strict enforcement of read-only operations
✅ **Real-Time Results** - Execute queries and get results instantly
✅ **Query Transparency** - See the generated MongoDB query alongside results
✅ **Error Handling** - Comprehensive validation and user-friendly error messages
✅ **Production-Ready** - Type-safe, validated, and containerized
✅ **Indexed Database** - Optimized MongoDB collection with strategic indexes

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- MongoDB URI (local or Atlas)
- Groq API Key (free tier available at https://console.groq.com)

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/sakshamsaxena22/LLMAutomatedDB.git
cd LLMAutomatedDB
```

2. **Create `.env` file in project root**
```bash
cat > .env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/payments?retryWrites=true&w=majority
# OR for local MongoDB:
# MONGODB_URI=mongodb://mongo:27017/payments

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Application Settings
MAX_RESULTS=100
EOF
```

3. **Start the application**
```bash
docker compose up --build
```

This will start:
- **Backend API**: http://localhost:8000 (FastAPI)
- **Frontend UI**: http://localhost:5173 (React Console)
- **MongoDB**: mongodb://localhost:27017 (if using local)

4. **Seed the database** (optional, if not auto-seeded)
```bash
# The seed data script will run automatically
# Or manually run:
docker compose exec backend python -m seed_data.seed_transaction
# Or for local development from the workspace root:
python -m backend.seed_data.seed_transaction
```

## 📊 API Endpoints

### Base URL: `http://localhost:8000`

#### 1. Query Endpoint
- **Endpoint**: `POST /query`
- **Description**: Convert natural language query to MongoDB query and fetch results
- **Content-Type**: `application/json`

**Request Body:**
```json
{
  "query": "Show all failed transactions"
}
```

**Response:**
```json
{
  "generated_query": {
    "filter": {"status": "FAILED"},
    "projection": null,
    "sort": [],
    "limit": 100
  },
  "count": 45,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "transaction_id": "TXN000001",
      "user_id": "USER001",
      "amount": 1500.00,
      "currency": "INR",
      "status": "FAILED",
      "merchant": "Amazon",
      "payment_method": "CARD",
      "timestamp": "2025-12-30T23:10:00Z"
    },
    ...
  ],
  "raw_response": { ... }
}
```

**Error Response (400):**
```json
{
  "detail": "Query cannot be safely generated"
}
```

## 💡 Usage Examples

### Web Interface (React Console)
1. Open http://localhost:5173
2. Enter natural language query in the text input
3. Click "Run Query" button
4. View generated MongoDB query and results in a formatted table

### Example Queries

**Example 1: Failed Transactions**
```
Query: "Show all failed transactions"
Generated: {"filter": {"status": "FAILED"}, "limit": 100}
```

**Example 2: High-Value Transactions**
```
Query: "Show transactions above 5000 INR"
Generated: {"filter": {"amount": {"$gt": 5000}}, "limit": 100}
```

**Example 3: Specific Merchant**
```
Query: "Show all Amazon transactions"
Generated: {"filter": {"merchant": "Amazon"}, "limit": 100}
```

**Example 4: Payment Method Filter**
```
Query: "Show UPI payments"
Generated: {"filter": {"payment_method": "UPI"}, "limit": 100}
```

**Example 5: Complex Query**
```
Query: "Show failed transactions from Uber above 2000"
Generated: {"filter": {"status": "FAILED", "merchant": "Uber", "amount": {"$gt": 2000}}, "limit": 100}
```

## 📁 Project Structure

```
LLMAutomatedDB/
├── backend/                    # FastAPI Backend
│   ├── app/                    # API source files (auth, users, ai, crud, database)
│   ├── prompts/                # Prompt templates (mongo_query_prompt.txt)
│   ├── seed_data/              # Database seeding scripts (seed_transaction.py)
│   ├── tests/                  # API test suites & legacy scripts
│   │   ├── legacy/             # Relocated quick debug scripts
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Docker container definition
├── frontend/                   # React Frontend (Vite + TS)
│   ├── src/                    # UI code (components, pages, routes, state hooks)
│   ├── Dockerfile              # Container building & deployment (Nginx)
│   └── nginx.conf              # Nginx server config & API proxy setup
├── docker-compose.yml          # Multi-container local orchestration
├── DEPLOYMENT.md               # Detailed deployment guide
├── .env.example               # Environment template
└── README.md                  # This file
````

## 🔒 Security Features

1. **Read-Only Enforcement**: Only SELECT/FIND operations allowed
2. **Query Validation**: All generated queries validated before execution
3. **Safe Prompting**: LLM instructed to refuse unsafe queries
4. **Error Handling**: Unsafe queries return explicit error responses
5. **Environment Isolation**: Sensitive credentials in .env files
6. **MongoDB Connection**: Authenticated connections with URI validation

## 🗄️ Database Schema

### Collection: `payments.transactions`

```javascript
{
  "_id": ObjectId,
  "transaction_id": "TXN000001",        // Unique transaction identifier
  "user_id": "USER001",                  // User identifier
  "amount": 1500.50,                     // Transaction amount
  "currency": "INR",                     // Currency code
  "status": "SUCCESS|FAILED|PENDING",    // Transaction status
  "merchant": "Amazon|Flipkart|...",     // Merchant name
  "payment_method": "UPI|CARD|NETBANKING", // Payment method
  "timestamp": ISODate("2025-12-30...")  // Transaction timestamp (UTC)
}
```

### Indexes
- `timestamp: DESCENDING` - Fast temporal queries
- `status: ASCENDING` - Status-based filtering
- `amount: ASCENDING` - Amount range queries
- `transaction_id: ASCENDING (UNIQUE)` - Unique constraint

## 🧪 Testing

```bash
# Run backend tests
docker compose exec backend pytest

# Run with coverage
docker compose exec backend pytest --cov=app
```

## 🐛 Troubleshooting

### Issue: "MONGODB_URI environment variable not set"
**Solution**: Ensure `.env` file exists in project root with valid MONGODB_URI

### Issue: "Groq API Key invalid"
**Solution**: Check GROQ_API_KEY in `.env` at https://console.groq.com

### Issue: Frontend cannot connect to backend
**Solution**: Verify backend service is running on port 8000
```bash
docker compose ps  # Check service status
docker compose logs backend  # View logs
```

### Issue: "Query cannot be safely generated"
**Solution**: Rephrase the query. The LLM may refuse unsafe queries like:
- DELETE/UPDATE operations
- Collection-wide access without filters
- Ambiguous or potentially harmful queries

## 📝 Configuration

All configuration is managed through environment variables in `.env`:

```bash
# MongoDB Connection
MONGODB_URI=mongodb://...

# LLM Provider
GROQ_API_KEY=...

# Application Limits
MAX_RESULTS=100  # Maximum results per query
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Saksham Saxena**  
GitHub: [@sakshamsaxena22](https://github.com/sakshamsaxena22)

## 🙏 Acknowledgments

- **Groq** - For the Llama 3.1 LLM API
- **MongoDB** - For the database platform
- **FastAPI** - For the modern web framework
- **Streamlit** - For the interactive UI framework

## 📞 Support

For issues, questions, or feedback, please open an issue on GitHub or contact the author.

---

**Made with ❤️ by Saksham Saxena**
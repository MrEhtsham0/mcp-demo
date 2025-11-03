# Expense Tracker AI

A modern expense tracking application built with FastAPI, LangGraph, MCP (Model Context Protocol), and Streamlit.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  LangGraph AI   │    │   FastAPI MCP   │
│                 │◄──►│     Agent       │◄──►│     Server      │
│  User Interface │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS RDS MySQL Database                      │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Set Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_HOST=expense-tracker-db.cx0aeuk0edcm.eu-north-1.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=expense_tracker
MYSQL_PASSWORD=expense-tracker-db
MYSQL_DATABASE=expense_tracker
```

### 3. Start Services

```bash
# Start both FastAPI and Streamlit
python main.py

# Start only FastAPI
python main.py --mode api

# Start only Streamlit
python main.py --mode frontend
```

## 🔧 Services

### FastAPI MCP Server (Port 8000)

- **Main API**: http://localhost:8000
- **MCP Endpoint**: http://localhost:8000/mcp
- **API Documentation**: http://localhost:8000/docs

### Streamlit App (Port 8501)

- **URL**: http://localhost:8501
- **Features**: Chat interface with AI agent

## 🤖 AI Agent Features

The LangGraph agent can help you with:

- **Adding Expenses**: "Add a $25 lunch expense for today"
- **Viewing Data**: "Show me all expenses from last month"
- **Summaries**: "Give me a breakdown by category"
- **Searching**: "Find all food expenses over $50"

## 📁 Project Structure

```
mcp-demo/
├── app/                          # Main application
│   ├── api/                      # API layer
│   │   ├── v1/endpoints/         # API endpoints
│   │   └── dependencies.py       # FastAPI dependencies
│   ├── core/                     # Core configuration
│   │   ├── config.py            # Settings
│   │   └── database.py          # Database connection
│   ├── models/                   # Database models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   ├── agents/                   # AI agents
│   └── app.py                    # FastAPI app
├── frontend/
│   └── streamlit_app.py         # Streamlit UI
├── tests/                        # Test suite
├── docker/                       # Docker configurations
├── main.py                       # Main entry point
└── pyproject.toml               # Dependencies
```

## 🧪 Testing

```bash
pytest tests/
```

## 🐳 Docker

```bash
# Build image
docker build -f docker/Dockerfile -t expense-tracker .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

## 📊 Database

The application uses AWS RDS MySQL with the following schema:

```sql
CREATE TABLE expenses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🔒 Security

- Set up AWS RDS security groups to allow port 3306
- Use environment variables for sensitive data
- Validate all user inputs

## 📄 License

MIT License

```
docker exec -it expense_tracker_mysql mysql -u root -p
```

## Advance Backend Technique

```
1=>Priority Implementation Order
2=>Observability (Logging, Metrics, Tracing) - Critical for production
3=>Security (Authentication, Input validation) - Security first
4=>Background Tasks - For scalability
5=>Event-Driven Architecture - For loose coupling
6=>Advanced Caching - For performance
7=>Database Optimization - For efficiency
8=>Circuit breaker for External sources.
9=>Background Task Processing

```

## Advance Caching Techniques

```
# Multi-level caching
class CacheStrategy:
    # L1: In-memory cache
    # L2: Redis cache
    # L3: Database

    async def get_with_fallback(self, key: str):
        # Try L1 -> L2 -> L3
        pass

# Cache warming
@celery_app.task
async def warm_cache():
    # Pre-populate frequently accessed data
    pass

# Cache invalidation patterns
class CacheInvalidator:
    async def invalidate_pattern(self, pattern: str):
        # Smart invalidation based on patterns
        pass
```

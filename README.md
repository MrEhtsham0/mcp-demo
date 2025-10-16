# Expense Tracker

A comprehensive expense tracking application with both MCP (Model Context Protocol) server and FastAPI REST API, supporting both SQLite and MySQL databases.

## Project Structure

```
mcp-demo/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── mcp_server.py          # MCP server implementation
│   │   └── fastapi_app.py         # FastAPI application
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                  # Database configuration and connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── expense.py             # Expense data model
│   └── services/
│       ├── __init__.py
│       └── expense_service.py     # Business logic for expenses
├── config.py                      # Application configuration
├── main.py                        # MCP server entry point
├── fastapi_server.py              # FastAPI server entry point
├── combined_server.py             # Combined MCP + FastAPI server
├── pyproject.toml                 # Project dependencies
└── env_template.txt               # Environment variables template
```

## Features

- **MCP Integration**: Full Model Context Protocol server implementation
- **FastAPI REST API**: Complete REST API with automatic documentation
- **Database Support**: Both SQLite (default) and MySQL support
- **ORM Queries**: SQLModel with Pydantic for type validation
- **Modular Architecture**: Clean separation of concerns
- **Docker Support**: MySQL running in Docker container

## Setup

1. **Install Dependencies**:

   ```bash
   pip install -e .
   ```

2. **Configure Environment**:

   ```bash
   cp env_template.txt .env
   # Edit .env with your database settings
   ```

3. **Run the Servers**:

   **MCP Server Only**:

   ```bash
   python main.py
   ```

   **FastAPI Server Only**:

   ```bash
   python fastapi_server.py
   ```

   **Both Servers**:

   ```bash
   python combined_server.py
   ```

## Database Configuration

### SQLite (Default)

The server uses SQLite by default. No additional setup required.

### MySQL (Optional)

To use MySQL, update your `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=expense_tracker
```

## MCP Tools

- `add_expense`: Add a new expense entry
- `list_expenses`: List expenses within a date range
- `list_all_expenses`: List all expenses
- `summarize`: Summarize expenses by category

## MCP Resources

- `expense:///categories`: Get available expense categories

## FastAPI Endpoints

### Base URL

- **Development**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### Endpoints

#### Expenses

- `POST /expenses/` - Create a new expense
- `GET /expenses/` - Get all expenses
- `GET /expenses/range/` - Get expenses within date range
- `GET /expenses/summary/` - Get expense summary by category
- `GET /expenses/{expense_id}` - Get specific expense
- `PUT /expenses/{expense_id}` - Update expense
- `DELETE /expenses/{expense_id}` - Delete expense

#### Categories

- `GET /categories/` - Get available expense categories

### Example Usage

```bash
# Create an expense
curl -X POST "http://localhost:8000/expenses/" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-15",
    "amount": 25.50,
    "category": "Food & Dining",
    "subcategory": "Lunch",
    "note": "Lunch at restaurant"
  }'

# Get all expenses
curl -X GET "http://localhost:8000/expenses/"

# Get expenses by date range
curl -X GET "http://localhost:8000/expenses/range/?start_date=2025-10-01&end_date=2025-10-31"

# Get expense summary
curl -X GET "http://localhost:8000/expenses/summary/?start_date=2025-10-01&end_date=2025-10-31"
```

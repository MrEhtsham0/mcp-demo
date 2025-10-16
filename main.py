from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.expense_route import expense_router
from fastmcp import FastMCP
import json
import os

# Create FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="A REST API for managing expenses with MCP integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the expense router
app.include_router(expense_router, prefix="/api")

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Expense Tracker API", "version": "1.0.0"}

# Convert FastAPI app to MCP server
mcp = FastMCP.from_fastapi(app=app)

# Add MCP Resources
@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    """Get available expense categories"""
    try:
        # Provide default categories if file doesn't exist
        default_categories = {
            "categories": [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Bills & Utilities",
                "Healthcare",
                "Travel",
                "Education",
                "Business",
                "Other"
            ]
        }
        
        categories_path = os.path.join(os.path.dirname(__file__), "categories.json")
        try:
            with open(categories_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return json.dumps(default_categories, indent=2)
    except Exception as e:
        return f'{{"error": "Could not load categories: {str(e)}"}}'

# Mount MCP to FastAPI app
app.mount("/mcp", mcp.from_fastapi(app=app))

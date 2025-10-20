"""
Unit tests for expense service
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.expense_service import ExpenseService
from app.models.expense import Expense

@pytest.mark.asyncio
async def test_create_expense_success(test_session, sample_expense):
    """Test successful expense creation"""
    service = ExpenseService(test_session)
    
    result = await service.create_expense(
        date=sample_expense["date"],
        amount=sample_expense["amount"],
        category=sample_expense["category"],
        subcategory=sample_expense["subcategory"],
        note=sample_expense["note"]
    )
    
    assert result["status"] == "success"
    assert "id" in result
    assert result["message"] == "Expense added successfully"

@pytest.mark.asyncio
async def test_create_expense_database_error():
    """Test expense creation with database error"""
    mock_session = AsyncMock()
    mock_session.add.side_effect = Exception("Database error")
    
    service = ExpenseService(mock_session)
    
    result = await service.create_expense(
        date="2024-01-15",
        amount=25.50,
        category="Food",
        subcategory="Lunch",
        note="Test"
    )
    
    assert result["status"] == "error"
    assert "Database error" in result["message"]

@pytest.mark.asyncio
async def test_get_all_expenses(test_session):
    """Test getting all expenses"""
    service = ExpenseService(test_session)
    
    # Add a test expense first
    await service.create_expense(
        date="2024-01-15",
        amount=25.50,
        category="Food",
        subcategory="Lunch",
        note="Test"
    )
    
    result = await service.get_all_expenses()
    
    assert isinstance(result, list)
    if result:  # If expenses exist
        assert "id" in result[0]
        assert "date" in result[0]
        assert "amount" in result[0]

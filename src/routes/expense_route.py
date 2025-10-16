from fastapi import APIRouter, Depends, HTTPException
from src.schema.expense_schema import ExpenseCreate, ExpenseResponse, ExpenseSummary
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.expense_service import ExpenseService
from src.models.expense import Expense
from typing import List, Optional
from src.database.db import get_async_session


expense_router = APIRouter()

@expense_router.post("/expenses/", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate, session: AsyncSession = Depends(get_async_session)):
    """Create a new expense"""
    try:
        result = await ExpenseService.create_expense(
            date=expense.date,
            amount=expense.amount,
            category=expense.category,
            subcategory=expense.subcategory,
            note=expense.note
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Get the created expense
        from sqlmodel import select
        statement = select(Expense).where(Expense.id == result["id"])
        result_query = await session.execute(statement)
        expense_obj = result_query.scalar_one_or_none()
        if not expense_obj:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        return expense_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@expense_router.get("/expenses/", response_model=List[ExpenseResponse])
async def get_all_expenses(session: AsyncSession = Depends(get_async_session)):
    """Get all expenses"""
    try:
        result = await ExpenseService.get_all_expenses()
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@expense_router.get("/expenses/range/", response_model=List[ExpenseResponse])
async def get_expenses_by_date_range(
    start_date: str,
    end_date: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get expenses within a date range"""
    try:
        result = await ExpenseService.get_expenses_by_date_range(start_date, end_date)
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@expense_router.get("/expenses/summary/", response_model=List[ExpenseSummary])
async def get_expense_summary(
    start_date: str,
    end_date: str,
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """Get expense summary by category"""
    try:
        result = await ExpenseService.summarize_expenses(start_date, end_date, category)
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@expense_router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, session: AsyncSession = Depends(get_async_session)):
    """Get a specific expense by ID"""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@expense_router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update an existing expense"""
    db_expense = session.get(Expense, expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update fields
    db_expense.date = expense.date
    db_expense.amount = expense.amount
    db_expense.category = expense.category
    db_expense.subcategory = expense.subcategory
    db_expense.note = expense.note
    
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    
    return db_expense

@expense_router.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int, session: AsyncSession = Depends(get_async_session)):
    """Delete an expense"""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    session.delete(expense)
    session.commit()
    
    return {"message": "Expense deleted successfully"}

@expense_router.get("/categories/")
async def get_categories():
    """Get available expense categories"""
    return {
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

# MCP setup is now handled in main.py
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from src.models.expense import Expense
from src.database.db import async_engine

class ExpenseService:
    """Service class for expense operations"""
    
    @staticmethod
    async def create_expense(
        date: str, 
        amount: float, 
        category: str, 
        subcategory: str = "", 
        note: str = ""
    ) -> Dict[str, Any]:
        """Create a new expense"""
        try:
            async with AsyncSession(async_engine) as session:
                expense = Expense(
                    date=date,
                    amount=amount,
                    category=category,
                    subcategory=subcategory,
                    note=note
                )
                session.add(expense)
                await session.commit()
                await session.refresh(expense)
                return {
                    "status": "success", 
                    "id": expense.id, 
                    "message": "Expense added successfully"
                }
        except Exception as e:
            return {"status": "error", "message": f"Database error: {str(e)}"}
    
    @staticmethod
    async def get_expenses_by_date_range(
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get expenses within a date range"""
        try:
            async with AsyncSession(async_engine) as session:
                statement = select(Expense).where(
                    Expense.date >= start_date,
                    Expense.date <= end_date
                ).order_by(Expense.date.desc(), Expense.id.desc())
                
                result = await session.execute(statement)
                expenses = result.scalars().all()
                
                return [
                    {
                        "id": expense.id,
                        "date": expense.date,
                        "amount": expense.amount,
                        "category": expense.category,
                        "subcategory": expense.subcategory,
                        "note": expense.note
                    }
                    for expense in expenses
                ]
        except Exception as e:
            return {"status": "error", "message": f"Error listing expenses: {str(e)}"}
    
    @staticmethod
    async def get_all_expenses() -> List[Dict[str, Any]]:
        """Get all expenses"""
        try:
            async with AsyncSession(async_engine) as session:
                statement = select(Expense).order_by(Expense.date.desc(), Expense.id.desc())
                result = await session.execute(statement)
                expenses = result.scalars().all()
                
                return [
                    {
                        "id": expense.id,
                        "date": expense.date,
                        "amount": expense.amount,
                        "category": expense.category,
                        "subcategory": expense.subcategory,
                        "note": expense.note
                    }
                    for expense in expenses
                ]
        except Exception as e:
            return {"status": "error", "message": f"Error listing expenses: {str(e)}"}
    
    @staticmethod
    async def summarize_expenses(
        start_date: str, 
        end_date: str, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Summarize expenses by category"""
        try:
            async with AsyncSession(async_engine) as session:
                statement = select(Expense).where(
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
                
                if category:
                    statement = statement.where(Expense.category == category)
                
                result = await session.execute(statement)
                expenses = result.scalars().all()
                
                # Group by category and calculate totals
                category_totals = {}
                for expense in expenses:
                    if expense.category not in category_totals:
                        category_totals[expense.category] = {"total_amount": 0, "count": 0}
                    category_totals[expense.category]["total_amount"] += expense.amount
                    category_totals[expense.category]["count"] += 1
                
                # Convert to list and sort by total amount
                summary = [
                    {
                        "category": cat,
                        "total_amount": data["total_amount"],
                        "count": data["count"]
                    }
                    for cat, data in category_totals.items()
                ]
                summary.sort(key=lambda x: x["total_amount"], reverse=True)
                
                return summary
        except Exception as e:
            return {"status": "error", "message": f"Error summarizing expenses: {str(e)}"}

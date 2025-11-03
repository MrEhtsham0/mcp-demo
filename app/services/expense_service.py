from sqlmodel import select
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.models.expense import Expense
from app.core.redis_cache import redis_cache, get_expense_pattern_key, get_expenses_pattern_key

class ExpenseService:
    """Service class for expense operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_expense(
        self,
        date: str, 
        amount: float, 
        category: str, 
        subcategory: str = "", 
        note: str = ""
    ) -> Dict[str, Any]:
        """Create a new expense with proper transaction handling"""
        try:
            expense = Expense(
                date=date,
                amount=amount,
                category=category,
                subcategory=subcategory,
                note=note
            )
            self.db.add(expense)
            await self.db.commit()
            await self.db.refresh(expense)
            
            return {
                "status": "success", 
                "id": expense.id, 
                "message": "Expense added successfully"
            }
        except Exception as e:
            await self.db.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}
    
    def get_expenses_by_date_range_query(
        self,
        start_date: str, 
        end_date: str
    ) -> Select:
        """Get query statement for expenses within a date range (for pagination)"""
        return select(Expense).where(
            Expense.date >= start_date,
            Expense.date <= end_date
        ).order_by(Expense.date.desc(), Expense.id.desc())
    
    async def get_expenses_by_date_range(
        self,
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get expenses within a date range with proper transaction handling (non-paginated, kept for backward compatibility)"""
        try:
            statement = select(Expense).where(
                Expense.date >= start_date,
                Expense.date <= end_date
            ).order_by(Expense.date.desc(), Expense.id.desc())
            
            result = await self.db.execute(statement)
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
    
    def get_all_expenses_query(self) -> Select:
        """Get query statement for all expenses (for pagination)"""
        return select(Expense).order_by(Expense.date.desc(), Expense.id.desc())
    
    async def get_all_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses with proper transaction handling (non-paginated, kept for backward compatibility)"""
        try:
            statement = select(Expense).order_by(Expense.date.desc(), Expense.id.desc())
            result = await self.db.execute(statement)
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
    
    async def summarize_expenses(
        self,
        start_date: str, 
        end_date: str, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Summarize expenses by category with proper transaction handling"""
        try:
            statement = select(Expense).where(
                Expense.date >= start_date,
                Expense.date <= end_date
            )
            
            if category:
                statement = statement.where(Expense.category == category)
            
            result = await self.db.execute(statement)
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
    
    async def invalidate_cache(self):
        """Invalidate all expense-related cache"""
        try:
            # Clear all expense-related cache keys
            await redis_cache.delete_pattern(get_expense_pattern_key())
            await redis_cache.delete_pattern(get_expenses_pattern_key())
        except Exception as e:
            print(f"Cache invalidation error: {e}")

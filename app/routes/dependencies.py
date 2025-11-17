"""
API dependencies
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.expense_service import ExpenseService
from app.db.database import get_async_session

async def get_expense_service(db: AsyncSession = Depends(get_async_session)) -> ExpenseService:
    """Get expense service instance with database session"""
    return ExpenseService(db)

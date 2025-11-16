"""
Expense API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate as apaginate
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseSummary
from app.services.expense_service import ExpenseService
from app.routes.dependencies import get_expense_service
from app.models.expense import Expense
from config import settings
from app.db.redis_cache import (
    redis_cache, 
    get_expense_key, 
    get_expense_summary_key,
)

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=ExpenseResponse)
@limiter.limit("4/minute")
async def create_expense(
    request: Request,
    expense: ExpenseCreate, 
    service: ExpenseService = Depends(get_expense_service)
):
    """Create a new expense"""
    try:
        result = await service.create_expense(
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
        from app.models.expense import Expense
        statement = select(Expense).where(Expense.id == result["id"])
        result_query = await service.db.execute(statement)
        expense_obj = result_query.scalar_one_or_none()
        if not expense_obj:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Invalidate cache after creating new expense
        await service.invalidate_cache()
        
        return expense_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Page[ExpenseResponse])
@limiter.limit("4/minute")
async def get_all_expenses(
    request: Request,
    params: Params = Depends(),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get all expenses with pagination and caching"""
    try:
        # Get paginated results directly from database
        # Note: Caching paginated results requires cache key to include page/size params
        statement = service.get_all_expenses_query()
        result = await apaginate(service.db, statement, params)
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/range/", response_model=Page[ExpenseResponse])
@limiter.limit("4/minute")
async def get_expenses_by_date_range(
    request: Request,
    start_date: str,
    end_date: str,
    params: Params = Depends(),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get expenses within a date range with pagination"""
    try:
        # Get paginated results directly from database
        statement = service.get_expenses_by_date_range_query(start_date, end_date)
        result = await apaginate(service.db, statement, params)
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/", response_model=List[ExpenseSummary])
@limiter.limit("4/minute")
async def get_expense_summary(
    request: Request,
    start_date: str,
    end_date: str,
    category: Optional[str] = None,
    service: ExpenseService = Depends(get_expense_service)
):
    """Get expense summary by category with caching"""
    try:
        # Try to get from cache first
        cache_key = get_expense_summary_key(start_date, end_date, category)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # If not in cache, get from database
        result = await service.summarize_expenses(start_date, end_date, category)
        
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Cache the result
        await redis_cache.set(cache_key, result, settings.cache_summary_ttl)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{expense_id}", response_model=ExpenseResponse)
@limiter.limit("4/minute")
async def get_expense(
    request: Request,
    expense_id: int, 
    service: ExpenseService = Depends(get_expense_service)
):
    """Get a specific expense by ID with caching"""
    try:
        # Try to get from cache first
        cache_key = get_expense_key(expense_id)
        cached_result = await redis_cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # If not in cache, get from database
        from sqlmodel import select
        statement = select(Expense).where(Expense.id == expense_id)
        result = await service.db.execute(statement)
        expense = result.scalar_one_or_none()
        
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Convert to dict for caching
        expense_dict = {
            "id": expense.id,
            "date": expense.date,
            "amount": expense.amount,
            "category": expense.category,
            "subcategory": expense.subcategory,
            "note": expense.note
        }
        
        # Cache the result
        await redis_cache.set(cache_key, expense_dict, settings.cache_expense_ttl)
        
        return expense_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{expense_id}", response_model=ExpenseResponse)
@limiter.limit("4/minute")
async def update_expense(
    request: Request,
    expense_id: int,
    expense: ExpenseCreate,
    service: ExpenseService = Depends(get_expense_service)
):
    """Update an existing expense"""
    from sqlmodel import select
    statement = select(Expense).where(Expense.id == expense_id)
    result = await service.db.execute(statement)
    db_expense = result.scalar_one_or_none()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update fields
    db_expense.date = expense.date
    db_expense.amount = expense.amount
    db_expense.category = expense.category
    db_expense.subcategory = expense.subcategory
    db_expense.note = expense.note
    
    service.db.add(db_expense)
    await service.db.commit()
    await service.db.refresh(db_expense)
    
    # Invalidate cache after updating expense
    await service.invalidate_cache()
    
    return db_expense

@router.delete("/{expense_id}")
@limiter.limit("4/minute")
async def delete_expense(
    request: Request,
    expense_id: int, 
    service: ExpenseService = Depends(get_expense_service)
):
    """Delete an expense"""
    from sqlmodel import select
    statement = select(Expense).where(Expense.id == expense_id)
    result = await service.db.execute(statement)
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    await service.db.delete(expense)
    await service.db.commit()
    
    # Invalidate cache after deleting expense
    await service.invalidate_cache()
    
    return {"message": "Expense deleted successfully"}

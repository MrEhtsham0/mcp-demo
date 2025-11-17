from pydantic import BaseModel

class ExpenseCreate(BaseModel):
    date: str
    amount: float
    category: str
    subcategory: str = ""
    note: str = ""

class ExpenseResponse(BaseModel):
    id: int
    date: str
    amount: float
    category: str
    subcategory: str
    note: str

    class ConfigDict:
        from_attributes = True

class ExpenseSummary(BaseModel):
    category: str
    total_amount: float
    count: int
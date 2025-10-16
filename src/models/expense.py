from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Expense(SQLModel, table=True):
    """Expense model for the expense tracker"""
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str = Field(index=True, description="Date of the expense")
    amount: float = Field(index=True, description="Amount of the expense")
    category: str = Field(index=True, description="Category of the expense")
    subcategory: str = Field(default="", description="Subcategory of the expense")
    note: str = Field(default="", description="Additional notes about the expense")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="When the expense was created")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="When the expense was last updated")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "amount": 25.50,
                "category": "Food & Dining",
                "subcategory": "Lunch",
                "note": "Lunch at restaurant"
            }
        }

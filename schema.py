from pydantic import BaseModel, Field

class ReceiptItem(BaseModel):
    item_name: str = Field(description="Name of the item")
    quantity: str | None = Field(default="1", description="Quantity of the item with unit")
    rate: float | None = Field(default=0.0, description="Rate per unit")
    total_price: float = Field(default=0.0, description="Total price for this line item")

class ReceiptData(BaseModel):
    vendor_name: str = Field(description="Vendor or shop name")
    date: str | None = Field(default="", description="Date of receipt")
    category: str = Field(default="General", description="Expense category like Grocery, Medical, etc.")
    items: list[ReceiptItem] = Field(default_factory=list, description="List of line items")
    grand_total: float = Field(default=0.0, description="Grand total expense amount")
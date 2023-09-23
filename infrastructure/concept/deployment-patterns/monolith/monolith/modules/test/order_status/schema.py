from typing import Union, List, Optional
from pydantic import Field, BaseModel

class OrderPiecesStatus(BaseModel):
    id: str
    created_at: str
    updated_at: str
    code: str
    contracts_failed: List[str] = Field(default_factory=list)
    node: Optional[str]
    observed_at: Optional[str]
    make_instance: int

class OrderStatus(BaseModel):
    created_at: str
    updated_at: str
    order_number: str
    code: str
    number: Optional[str]
    sku: str
    one_pieces: List[OrderPiecesStatus] = Field(default_factory=list)
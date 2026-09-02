from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, computed_field

class Supply(BaseModel):
    sku: str
    supply_name: Optional[str] = None
    category: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    supplier_id: Optional[str] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None

class Inventory(BaseModel):
    sku: str
    on_hand: Optional[int] = None
    reserved: Optional[int] = None

    @computed_field
    @property
    def available(self) -> Optional[int]:
        if self.on_hand is None or self.reserved is None:
            return None
        return self.on_hand - self.reserved

class PurchaseOrder(BaseModel):
    purchase_order_id: str
    sku: Optional[str] = None
    supplier_id: Optional[str] = None
    quantity_ordered: Optional[int] = None
    quantity_received: Optional[int] = None
    order_date: Optional[date] = None
    expected_date: Optional[date] = None
    status: Optional[str] = None

class SalesOrder(BaseModel):
    sales_order_id: str
    sku: Optional[str] = None
    quantity_ordered: Optional[int] = None
    quantity_shipped: Optional[int] = None
    order_date: Optional[date] = None
    requested_date: Optional[date] = None
    status: Optional[str] = None

class Shipment(BaseModel):
    shipment_id: str
    sku: Optional[str] = None
    purchase_order_id: Optional[str] = None
    sales_order_id: Optional[str] = None
    quantity: Optional[int] = None
    shipment_type: Optional[str] = None
    ship_date: Optional[date] = None
    expected_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: Optional[str] = None

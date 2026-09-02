from decimal import Decimal
from typing import Optional

from langchain_core.tools import tool

from app.db.supplies import query_supplies

@tool
def get_supplies(
    sku: Optional[str] = None,
    supply_name: Optional[str] = None,
    category: Optional[str] = None,
    unit_cost: Optional[Decimal] = None,
    supplier_id: Optional[str] = None,
    reorder_point: Optional[int] = None,
    reorder_quantity: Optional[int] = None
) -> dict:
    '''
    Get supply catalog records matching the given filters. Provide at least
    one argument; results must match all arguments provided.

    Args:
        sku: The stock keeping unit to look up.
        supply_name: The name of the supply.
        category: The category the supply belongs to.
        unit_cost: Filter to supplies with this unit cost.
        supplier_id: The supplier that provides the supply.
        reorder_point: Filter to supplies with this reorder point.
        reorder_quantity: Filter to supplies with this reorder quantity.
    '''

    if all(value is None for value in (
        sku,
        supply_name,
        category,
        unit_cost,
        supplier_id,
        reorder_point,
        reorder_quantity
    )):
        return {
            'message': 'Please provide at least one filter.'
        }

    supplies = query_supplies(
        sku,
        supply_name,
        category,
        unit_cost,
        supplier_id,
        reorder_point,
        reorder_quantity
    )

    if not supplies:
        return {
            'sku': sku,
            'supply_name': supply_name,
            'category': category,
            'unit_cost': unit_cost,
            'supplier_id': supplier_id,
            'reorder_point': reorder_point,
            'reorder_quantity': reorder_quantity,
            'supplies': [],
            'message': 'No supplies found.'
        }

    return {
        'sku': sku,
        'supply_name': supply_name,
        'category': category,
        'unit_cost': unit_cost,
        'supplier_id': supplier_id,
        'reorder_point': reorder_point,
        'reorder_quantity': reorder_quantity,
        'supplies': [
            supply.model_dump(mode='json')
            for supply in supplies
        ]
    }

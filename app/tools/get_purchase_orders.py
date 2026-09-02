from datetime import date
from typing import Optional

from langchain_core.tools import tool

from app.db.purchase_orders import query_purchase_orders

@tool
def get_purchase_orders(
    purchase_order_id: Optional[str] = None,
    sku: Optional[str] = None,
    supplier_id: Optional[str] = None,
    quantity_ordered: Optional[int] = None,
    quantity_received: Optional[int] = None,
    order_date: Optional[date] = None,
    expected_date: Optional[date] = None,
    status: Optional[str] = None
) -> dict:
    '''
    Get purchase orders matching the given filters. Provide at least one
    argument; results must match all arguments provided.

    Args:
        purchase_order_id: The purchase order identifier to look up.
        sku: The stock keeping unit the order is for.
        supplier_id: The supplier the order was placed with.
        quantity_ordered: Filter to orders with this ordered quantity.
        quantity_received: Filter to orders with this received quantity.
        order_date: Filter to orders placed on this date.
        expected_date: Filter to orders expected on this date.
        status: Filter to orders in this status.
    '''

    if all(value is None for value in (
        purchase_order_id,
        sku,
        supplier_id,
        quantity_ordered,
        quantity_received,
        order_date,
        expected_date,
        status
    )):
        return {
            'message': 'Please provide at least one filter.'
        }

    purchase_orders = query_purchase_orders(
        purchase_order_id,
        sku,
        supplier_id,
        quantity_ordered,
        quantity_received,
        order_date,
        expected_date,
        status
    )

    if not purchase_orders:
        return {
            'purchase_order_id': purchase_order_id,
            'sku': sku,
            'supplier_id': supplier_id,
            'quantity_ordered': quantity_ordered,
            'quantity_received': quantity_received,
            'order_date': order_date,
            'expected_date': expected_date,
            'status': status,
            'purchase_orders': [],
            'message': 'No purchase orders found.'
        }

    return {
        'purchase_order_id': purchase_order_id,
        'sku': sku,
        'supplier_id': supplier_id,
        'quantity_ordered': quantity_ordered,
        'quantity_received': quantity_received,
        'order_date': order_date,
        'expected_date': expected_date,
        'status': status,
        'purchase_orders': [
            purchase_order.model_dump(mode='json')
            for purchase_order in purchase_orders
        ]
    }

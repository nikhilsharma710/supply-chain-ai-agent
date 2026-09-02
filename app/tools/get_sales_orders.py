from datetime import date
from typing import Optional

from langchain_core.tools import tool

from app.db.sales_orders import query_sales_orders

@tool
def get_sales_orders(
    sales_order_id: Optional[str] = None,
    sku: Optional[str] = None,
    quantity_ordered: Optional[int] = None,
    quantity_shipped: Optional[int] = None,
    order_date: Optional[date] = None,
    requested_date: Optional[date] = None,
    status: Optional[str] = None
) -> dict:
    '''
    Get sales orders matching the given filters. Provide at least one
    argument; results must match all arguments provided.

    Args:
        sales_order_id: The sales order identifier to look up.
        sku: The stock keeping unit the order is for.
        quantity_ordered: Filter to orders with this ordered quantity.
        quantity_shipped: Filter to orders with this shipped quantity.
        order_date: Filter to orders placed on this date.
        requested_date: Filter to orders requested for this date.
        status: Filter to orders in this status.
    '''

    if all(value is None for value in (
        sales_order_id,
        sku,
        quantity_ordered,
        quantity_shipped,
        order_date,
        requested_date,
        status
    )):
        return {
            'message': 'Please provide at least one filter.'
        }

    sales_orders = query_sales_orders(
        sales_order_id,
        sku,
        quantity_ordered,
        quantity_shipped,
        order_date,
        requested_date,
        status
    )

    if not sales_orders:
        return {
            'sales_order_id': sales_order_id,
            'sku': sku,
            'quantity_ordered': quantity_ordered,
            'quantity_shipped': quantity_shipped,
            'order_date': order_date,
            'requested_date': requested_date,
            'status': status,
            'sales_orders': [],
            'message': 'No sales orders found.'
        }

    return {
        'sales_order_id': sales_order_id,
        'sku': sku,
        'quantity_ordered': quantity_ordered,
        'quantity_shipped': quantity_shipped,
        'order_date': order_date,
        'requested_date': requested_date,
        'status': status,
        'sales_orders': [
            sales_order.model_dump(mode='json')
            for sales_order in sales_orders
        ]
    }

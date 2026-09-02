from datetime import date
from typing import Optional

from langchain_core.tools import tool

from app.db.shipments import query_shipments

@tool
def get_shipments(
    shipment_id: Optional[str] = None,
    sku: Optional[str] = None,
    purchase_order_id: Optional[str] = None,
    sales_order_id: Optional[str] = None,
    quantity: Optional[int] = None,
    shipment_type: Optional[str] = None,
    ship_date: Optional[date] = None,
    expected_date: Optional[date] = None,
    delivery_date: Optional[date] = None,
    status: Optional[str] = None
) -> dict:
    '''
    Get shipments matching the given filters. Provide at least one
    argument; results must match all arguments provided.

    Args:
        shipment_id: The shipment identifier to look up.
        sku: The stock keeping unit the shipment is for.
        purchase_order_id: The purchase order this shipment fulfils.
        sales_order_id: The sales order this shipment fulfils.
        quantity: Filter to shipments of this quantity.
        shipment_type: Filter to shipments of this type (e.g. inbound, outbound).
        ship_date: Filter to shipments sent on this date.
        expected_date: Filter to shipments expected on this date.
        delivery_date: Filter to shipments delivered on this date.
        status: Filter to shipments in this status.
    '''

    if all(value is None for value in (
        shipment_id,
        sku,
        purchase_order_id,
        sales_order_id,
        quantity,
        shipment_type,
        ship_date,
        expected_date,
        delivery_date,
        status
    )):
        return {
            'message': 'Please provide at least one filter.'
        }

    shipments = query_shipments(
        shipment_id,
        sku,
        purchase_order_id,
        sales_order_id,
        quantity,
        shipment_type,
        ship_date,
        expected_date,
        delivery_date,
        status
    )

    if not shipments:
        return {
            'shipment_id': shipment_id,
            'sku': sku,
            'purchase_order_id': purchase_order_id,
            'sales_order_id': sales_order_id,
            'quantity': quantity,
            'shipment_type': shipment_type,
            'ship_date': ship_date,
            'expected_date': expected_date,
            'delivery_date': delivery_date,
            'status': status,
            'shipments': [],
            'message': 'No shipments found.'
        }

    return {
        'shipment_id': shipment_id,
        'sku': sku,
        'purchase_order_id': purchase_order_id,
        'sales_order_id': sales_order_id,
        'quantity': quantity,
        'shipment_type': shipment_type,
        'ship_date': ship_date,
        'expected_date': expected_date,
        'delivery_date': delivery_date,
        'status': status,
        'shipments': [
            shipment.model_dump(mode='json')
            for shipment in shipments
        ]
    }

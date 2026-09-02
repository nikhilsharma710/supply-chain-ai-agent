from datetime import date
from typing import Optional

from psycopg2.extras import RealDictCursor

from app.db.connection import get_connection
from app.models.schemas import Shipment

def query_shipments(
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
) -> list[Shipment]:
    '''Query shipments using one or more filters.'''

    filters = {
        'shipment_id': shipment_id,
        'sku': sku,
        'purchase_order_id': purchase_order_id,
        'sales_order_id': sales_order_id,
        'quantity': quantity,
        'shipment_type': shipment_type,
        'ship_date': ship_date,
        'expected_date': expected_date,
        'delivery_date': delivery_date,
        'status': status
    }

    conditions = []
    params = []

    for column, value in filters.items():
        if value is not None:
            conditions.append(f'{column} = %s')
            params.append(value)

    if not conditions:
        return []

    clause = ' AND '.join(conditions)

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f'SELECT * FROM shipments WHERE {clause}', params)

                rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        Shipment.model_validate(dict(row))
        for row in rows
    ]

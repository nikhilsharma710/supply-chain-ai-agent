from datetime import date
from typing import Optional

from psycopg2.extras import RealDictCursor

from app.db.connection import get_connection
from app.models.schemas import PurchaseOrder

def query_purchase_orders(
    purchase_order_id: Optional[str] = None,
    sku: Optional[str] = None,
    supplier_id: Optional[str] = None,
    quantity_ordered: Optional[int] = None,
    quantity_received: Optional[int] = None,
    order_date: Optional[date] = None,
    expected_date: Optional[date] = None,
    status: Optional[str] = None
) -> list[PurchaseOrder]:
    '''Query purchase orders using one or more filters.'''

    filters = {
        'purchase_order_id': purchase_order_id,
        'sku': sku,
        'supplier_id': supplier_id,
        'quantity_ordered': quantity_ordered,
        'quantity_received': quantity_received,
        'order_date': order_date,
        'expected_date': expected_date,
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
                cursor.execute(f'SELECT * FROM purchase_orders WHERE {clause}', params)

                rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        PurchaseOrder.model_validate(dict(row))
        for row in rows
    ]

from datetime import date
from typing import Optional

from psycopg2.extras import RealDictCursor

from app.db.connection import get_connection
from app.models.schemas import SalesOrder

def query_sales_orders(
    sales_order_id: Optional[str] = None,
    sku: Optional[str] = None,
    quantity_ordered: Optional[int] = None,
    quantity_shipped: Optional[int] = None,
    order_date: Optional[date] = None,
    requested_date: Optional[date] = None,
    status: Optional[str] = None
) -> list[SalesOrder]:
    '''Query sales orders using one or more filters.'''

    filters = {
        'sales_order_id': sales_order_id,
        'sku': sku,
        'quantity_ordered': quantity_ordered,
        'quantity_shipped': quantity_shipped,
        'order_date': order_date,
        'requested_date': requested_date,
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
                cursor.execute(f'SELECT * FROM sales_orders WHERE {clause}', params)

                rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        SalesOrder.model_validate(dict(row))
        for row in rows
    ]

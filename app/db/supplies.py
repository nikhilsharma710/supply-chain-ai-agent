from decimal import Decimal
from typing import Optional

from psycopg2.extras import RealDictCursor

from app.db.connection import get_connection
from app.models.schemas import Supply

def query_supplies(
    sku: Optional[str] = None,
    supply_name: Optional[str] = None,
    category: Optional[str] = None,
    unit_cost: Optional[Decimal] = None,
    supplier_id: Optional[str] = None,
    reorder_point: Optional[int] = None,
    reorder_quantity: Optional[int] = None
) -> list[Supply]:
    '''Query supplies using one or more filters.'''

    filters = {
        'sku': sku,
        'supply_name': supply_name,
        'category': category,
        'unit_cost': unit_cost,
        'supplier_id': supplier_id,
        'reorder_point': reorder_point,
        'reorder_quantity': reorder_quantity
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
                cursor.execute(f'SELECT * FROM supplies WHERE {clause}', params)

                rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        Supply.model_validate(dict(row))
        for row in rows
    ]

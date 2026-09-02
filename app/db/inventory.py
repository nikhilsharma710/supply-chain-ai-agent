from typing import Optional

from psycopg2.extras import RealDictCursor

from app.db.connection import get_connection
from app.models.schemas import Inventory

def query_inventory(
    sku: Optional[str] = None,
    on_hand: Optional[int] = None,
    reserved: Optional[int] = None
) -> list[Inventory]:
    '''Query inventory using one or more filters.'''

    filters = {
        'sku': sku,
        'on_hand': on_hand,
        'reserved': reserved
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
                cursor.execute(f'SELECT * FROM inventory WHERE {clause}', params)

                rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        Inventory.model_validate(dict(row))
        for row in rows
    ]

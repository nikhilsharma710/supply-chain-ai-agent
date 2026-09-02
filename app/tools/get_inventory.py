from typing import Optional

from langchain_core.tools import tool

from app.db.inventory import query_inventory

@tool
def get_inventory(
    sku: Optional[str] = None,
    on_hand: Optional[int] = None,
    reserved: Optional[int] = None
) -> dict:
    '''
    Get inventory records matching the given filters. Provide at least one
    argument; results must match all arguments provided.

    Args:
        sku: The stock keeping unit to look up.
        on_hand: Filter to records with this on-hand quantity.
        reserved: Filter to records with this reserved quantity.
    '''

    if all(value is None for value in (sku, on_hand, reserved)):
        return {
            'message': 'Please provide at least one filter.'
        }

    inventory = query_inventory(sku, on_hand, reserved)

    if not inventory:
        return {
            'sku': sku,
            'on_hand': on_hand,
            'reserved': reserved,
            'inventory': [],
            'message': 'No inventory found.'
        }

    return {
        'sku': sku,
        'on_hand': on_hand,
        'reserved': reserved,
        'inventory': [
            record.model_dump(mode='json')
            for record in inventory
        ]
    }

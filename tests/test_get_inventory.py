'''Test for the ``get_inventory`` tool.

Drives the tool end to end against the live ``supply_chain`` database and
pins its output to a known row. The ``database`` fixture skips this when the
database is unreachable.
'''

from app.tools.get_inventory import get_inventory


def test_get_inventory(database):
    result = get_inventory.invoke({'sku': 'SKU-0001'})

    assert result['inventory'] == [
        {'sku': 'SKU-0001', 'on_hand': 1087, 'reserved': 237, 'available': 850},
    ]

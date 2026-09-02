'''Test for the ``get_supplies`` tool.

Drives the tool end to end against the live ``supply_chain`` database and
pins its output to a known row. The ``database`` fixture skips this when the
database is unreachable.
'''

from app.tools.get_supplies import get_supplies


def test_get_supplies(database):
    result = get_supplies.invoke({'sku': 'SKU-0001'})

    assert result['supplies'] == [
        {
            'sku': 'SKU-0001',
            'supply_name': 'Standard Resin',
            'category': 'Hardware',
            'unit_cost': '220.92',
            'supplier_id': 'SUP-0002',
            'reorder_point': 499,
            'reorder_quantity': 565,
        },
    ]

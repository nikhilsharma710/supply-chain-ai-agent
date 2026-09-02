'''Test for the ``get_purchase_orders`` tool.

Drives the tool end to end against the live ``supply_chain`` database and
pins its output to a known row. The ``database`` fixture skips this when the
database is unreachable.
'''

from app.tools.get_purchase_orders import get_purchase_orders


def test_get_purchase_orders(database):
    result = get_purchase_orders.invoke({'purchase_order_id': 'PO-0001'})

    assert result['purchase_orders'] == [
        {
            'purchase_order_id': 'PO-0001',
            'sku': 'SKU-0039',
            'supplier_id': 'SUP-0008',
            'quantity_ordered': 2689,
            'quantity_received': 0,
            'order_date': '2026-04-21',
            'expected_date': '2026-05-25',
            'status': 'cancelled',
        },
    ]

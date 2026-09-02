'''Test for the ``get_shipments`` tool.

Drives the tool end to end against the live ``supply_chain`` database and
pins its output to a known row. The ``database`` fixture skips this when the
database is unreachable.
'''

from app.tools.get_shipments import get_shipments


def test_get_shipments(database):
    result = get_shipments.invoke({'shipment_id': 'SH-0001'})

    assert result['shipments'] == [
        {
            'shipment_id': 'SH-0001',
            'sku': 'SKU-0010',
            'purchase_order_id': None,
            'sales_order_id': 'SO-0021',
            'quantity': 2744,
            'shipment_type': 'outbound',
            'ship_date': '2026-12-14',
            'expected_date': '2026-12-30',
            'delivery_date': None,
            'status': 'created',
        },
    ]

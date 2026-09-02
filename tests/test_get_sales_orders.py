'''Test for the ``get_sales_orders`` tool.

Drives the tool end to end against the live ``supply_chain`` database and
pins its output to a known row. The ``database`` fixture skips this when the
database is unreachable.
'''

from app.tools.get_sales_orders import get_sales_orders


def test_get_sales_orders(database):
    result = get_sales_orders.invoke({'sales_order_id': 'SO-0001'})

    assert result['sales_orders'] == [
        {
            'sales_order_id': 'SO-0001',
            'sku': 'SKU-0019',
            'quantity_ordered': 1223,
            'quantity_shipped': 332,
            'order_date': '2026-05-30',
            'requested_date': '2026-07-06',
            'status': 'processing',
        },
    ]

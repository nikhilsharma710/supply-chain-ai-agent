'''Tests for the LangChain tools in ``app.tools``.

These run against the live ``supply_chain`` Postgres database configured in
``.env``. The assertions below are pinned to rows that exist in that
database. If the database cannot be reached the whole module is skipped so
the suite stays usable on machines without it.
'''

from decimal import Decimal

import pytest

from app.db.connection import get_connection
from app.tools.get_inventory import get_inventory
from app.tools.get_purchase_orders import get_purchase_orders
from app.tools.get_sales_orders import get_sales_orders
from app.tools.get_shipments import get_shipments
from app.tools.get_supplies import get_supplies


def _database_available() -> bool:
    try:
        conn = get_connection()
    except Exception:
        return False
    conn.close()
    return True


pytestmark = pytest.mark.skipif(
    not _database_available(),
    reason='supply_chain database is not reachable',
)


# --------------------------------------------------------------------------- #
# get_inventory
# --------------------------------------------------------------------------- #

def test_get_inventory_by_sku_returns_single_record():
    result = get_inventory.invoke({'sku': 'SKU-0001'})

    assert result['inventory'] == [
        {'sku': 'SKU-0001', 'on_hand': 1087, 'reserved': 237, 'available': 850},
    ]


def test_get_inventory_available_is_on_hand_minus_reserved():
    (record,) = get_inventory.invoke({'sku': 'SKU-0026'})['inventory']

    assert record['on_hand'] == 4793
    assert record['reserved'] == 1530
    assert record['available'] == record['on_hand'] - record['reserved']


def test_get_inventory_without_filters_asks_for_one():
    result = get_inventory.invoke({})

    assert result == {'message': 'Please provide at least one filter.'}


def test_get_inventory_unknown_sku_reports_no_match():
    result = get_inventory.invoke({'sku': 'SKU-9999'})

    assert result['inventory'] == []
    assert result['message'] == 'No inventory found.'


# --------------------------------------------------------------------------- #
# get_supplies
# --------------------------------------------------------------------------- #

def test_get_supplies_by_sku():
    (supply,) = get_supplies.invoke({'sku': 'SKU-0001'})['supplies']

    assert supply == {
        'sku': 'SKU-0001',
        'supply_name': 'Standard Resin',
        'category': 'Hardware',
        'unit_cost': '220.92',
        'supplier_id': 'SUP-0002',
        'reorder_point': 499,
        'reorder_quantity': 565,
    }


def test_get_supplies_by_supplier_returns_all_five():
    supplies = get_supplies.invoke({'supplier_id': 'SUP-0001'})['supplies']

    assert {s['sku'] for s in supplies} == {
        'SKU-0008', 'SKU-0010', 'SKU-0013', 'SKU-0035', 'SKU-0036',
    }


def test_get_supplies_unit_cost_filter_accepts_decimal():
    supplies = get_supplies.invoke({'unit_cost': Decimal('949.28')})['supplies']

    assert [s['sku'] for s in supplies] == ['SKU-0040']


def test_get_supplies_without_filters_asks_for_one():
    assert get_supplies.invoke({}) == {'message': 'Please provide at least one filter.'}


# --------------------------------------------------------------------------- #
# get_purchase_orders
# --------------------------------------------------------------------------- #

def test_get_purchase_orders_by_id():
    (order,) = get_purchase_orders.invoke(
        {'purchase_order_id': 'PO-0001'}
    )['purchase_orders']

    assert order == {
        'purchase_order_id': 'PO-0001',
        'sku': 'SKU-0039',
        'supplier_id': 'SUP-0008',
        'quantity_ordered': 2689,
        'quantity_received': 0,
        'order_date': '2026-04-21',
        'expected_date': '2026-05-25',
        'status': 'cancelled',
    }


def test_get_purchase_orders_by_sku():
    orders = get_purchase_orders.invoke({'sku': 'SKU-0002'})['purchase_orders']

    assert {o['purchase_order_id'] for o in orders} == {'PO-0003', 'PO-0011'}


def test_get_purchase_orders_by_status():
    orders = get_purchase_orders.invoke({'status': 'received'})['purchase_orders']

    assert {o['purchase_order_id'] for o in orders} == {
        'PO-0012', 'PO-0019', 'PO-0020', 'PO-0023',
    }


def test_get_purchase_orders_unknown_id_reports_no_match():
    result = get_purchase_orders.invoke({'purchase_order_id': 'PO-9999'})

    assert result['purchase_orders'] == []
    assert result['message'] == 'No purchase orders found.'


# --------------------------------------------------------------------------- #
# get_sales_orders
# --------------------------------------------------------------------------- #

def test_get_sales_orders_by_id():
    (order,) = get_sales_orders.invoke(
        {'sales_order_id': 'SO-0001'}
    )['sales_orders']

    assert order == {
        'sales_order_id': 'SO-0001',
        'sku': 'SKU-0019',
        'quantity_ordered': 1223,
        'quantity_shipped': 332,
        'order_date': '2026-05-30',
        'requested_date': '2026-07-06',
        'status': 'processing',
    }


def test_get_sales_orders_by_sku():
    orders = get_sales_orders.invoke({'sku': 'SKU-0019'})['sales_orders']

    assert {o['sales_order_id'] for o in orders} == {'SO-0001', 'SO-0023'}


def test_get_sales_orders_shipped_status_count():
    orders = get_sales_orders.invoke({'status': 'shipped'})['sales_orders']

    assert len(orders) == 11
    assert all(o['status'] == 'shipped' for o in orders)


# --------------------------------------------------------------------------- #
# get_shipments
# --------------------------------------------------------------------------- #

def test_get_shipments_by_id():
    (shipment,) = get_shipments.invoke({'shipment_id': 'SH-0001'})['shipments']

    assert shipment == {
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
    }


def test_get_shipments_by_sku():
    shipments = get_shipments.invoke({'sku': 'SKU-0032'})['shipments']

    assert {s['shipment_id'] for s in shipments} == {
        'SH-0004', 'SH-0011', 'SH-0021', 'SH-0030',
    }


def test_get_shipments_delayed_status_count():
    shipments = get_shipments.invoke({'status': 'delayed'})['shipments']

    assert len(shipments) == 9
    assert all(s['status'] == 'delayed' for s in shipments)


def test_get_shipments_inbound_linked_to_purchase_orders():
    shipments = get_shipments.invoke({'shipment_type': 'inbound'})['shipments']

    assert len(shipments) == 13
    assert all(s['purchase_order_id'] is not None for s in shipments)
    assert all(s['sales_order_id'] is None for s in shipments)


def test_get_shipments_without_filters_asks_for_one():
    assert get_shipments.invoke({}) == {'message': 'Please provide at least one filter.'}

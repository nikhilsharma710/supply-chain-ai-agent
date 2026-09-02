'''Tests for the LangGraph agent wiring in ``app.agent``.

The graph-structure and routing tests need no network. ``call_tools``
executes the real tools, so those cases hit the live ``supply_chain``
database and are skipped when it is unreachable.
'''

import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END

from app.agent.graph import build_graph, should_continue
from app.agent.nodes import TOOLS, call_tools
from app.db.connection import get_connection


def _database_available() -> bool:
    try:
        conn = get_connection()
    except Exception:
        return False
    conn.close()
    return True


requires_database = pytest.mark.skipif(
    not _database_available(),
    reason='supply_chain database is not reachable',
)


def _tool_call(name: str, args: dict, call_id: str = 'call_1') -> dict:
    return {'name': name, 'args': args, 'id': call_id, 'type': 'tool_call'}


# --------------------------------------------------------------------------- #
# routing
# --------------------------------------------------------------------------- #

def test_should_continue_routes_to_tools_when_tool_calls_present():
    message = AIMessage(
        content='',
        tool_calls=[_tool_call('get_inventory', {'sku': 'SKU-0001'})],
    )

    assert should_continue({'messages': [message]}) == 'tools'


def test_should_continue_ends_on_plain_response():
    message = AIMessage(content='Here is your answer.')

    assert should_continue({'messages': [message]}) == END


def test_should_continue_ends_on_human_message():
    assert should_continue({'messages': [HumanMessage(content='hi')]}) == END


# --------------------------------------------------------------------------- #
# graph structure
# --------------------------------------------------------------------------- #

def test_build_graph_compiles_with_agent_and_tools_nodes():
    graph = build_graph()

    assert {'agent', 'tools'} <= set(graph.get_graph().nodes)


def test_registered_tools_match_expected_names():
    assert sorted(tool.name for tool in TOOLS) == [
        'get_inventory',
        'get_purchase_orders',
        'get_sales_orders',
        'get_shipments',
        'get_supplies',
    ]


# --------------------------------------------------------------------------- #
# call_tools
# --------------------------------------------------------------------------- #

@requires_database
def test_call_tools_executes_requested_tool_against_database():
    message = AIMessage(
        content='',
        tool_calls=[_tool_call('get_supplies', {'sku': 'SKU-0001'})],
    )

    result = call_tools({'messages': [message]})

    (tool_message,) = result['messages']
    assert tool_message['role'] == 'tool'
    assert tool_message['tool_call_id'] == 'call_1'

    payload = json.loads(tool_message['content'])
    assert payload['supplies'][0]['supply_name'] == 'Standard Resin'
    assert payload['supplies'][0]['category'] == 'Hardware'


@requires_database
def test_call_tools_handles_multiple_tool_calls():
    message = AIMessage(
        content='',
        tool_calls=[
            _tool_call('get_inventory', {'sku': 'SKU-0001'}, 'a'),
            _tool_call('get_sales_orders', {'sales_order_id': 'SO-0001'}, 'b'),
        ],
    )

    result = call_tools({'messages': [message]})

    assert [m['tool_call_id'] for m in result['messages']] == ['a', 'b']


def test_call_tools_raises_on_unknown_tool():
    message = AIMessage(
        content='',
        tool_calls=[_tool_call('get_weather', {'city': 'Denver'})],
    )

    with pytest.raises(ValueError, match='Unknown tool requested: get_weather'):
        call_tools({'messages': [message]})

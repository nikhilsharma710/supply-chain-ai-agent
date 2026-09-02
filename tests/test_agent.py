'''Tests for the agent layer in ``app.agent``.

Scope is limited to behaviour that belongs to the agent itself: conditional
routing, graph construction, the tool registry, and how ``call_tools``
dispatches and wraps tool results. The tools' own output is covered by the
``test_get_*`` modules and is not re-checked here.
'''

import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END

from app.agent.graph import build_graph, should_continue
from app.agent.nodes import TOOLS, call_tools


def _tool_call(name: str, args: dict, call_id: str = 'call_1') -> dict:
    return {'name': name, 'args': args, 'id': call_id, 'type': 'tool_call'}


# --------------------------------------------------------------------------- #
# should_continue
# --------------------------------------------------------------------------- #

def test_should_continue_routes_to_tools_when_the_model_requests_one():
    message = AIMessage(
        content='',
        tool_calls=[_tool_call('get_inventory', {'sku': 'SKU-0001'})],
    )

    assert should_continue({'messages': [message]}) == 'tools'


def test_should_continue_ends_when_the_last_message_has_no_tool_calls():
    assert should_continue({'messages': [AIMessage(content='Done.')]}) == END
    assert should_continue({'messages': [HumanMessage(content='hi')]}) == END


# --------------------------------------------------------------------------- #
# graph / registry
# --------------------------------------------------------------------------- #

def test_build_graph_wires_the_agent_and_tools_nodes():
    graph = build_graph()

    assert {'agent', 'tools'} <= set(graph.get_graph().nodes)


def test_tool_registry_exposes_the_five_supply_chain_tools():
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

def test_call_tools_dispatches_and_wraps_each_result_as_a_tool_message(database):
    message = AIMessage(
        content='',
        tool_calls=[
            _tool_call('get_inventory', {'sku': 'SKU-0001'}, 'a'),
            _tool_call('get_sales_orders', {'sales_order_id': 'SO-0001'}, 'b'),
        ],
    )

    messages = call_tools({'messages': [message]})['messages']

    assert [m['role'] for m in messages] == ['tool', 'tool']
    assert [m['tool_call_id'] for m in messages] == ['a', 'b']
    # content is the JSON-serialised tool result, ready to hand back to the model.
    assert all(isinstance(json.loads(m['content']), dict) for m in messages)


def test_call_tools_raises_on_an_unregistered_tool():
    message = AIMessage(
        content='',
        tool_calls=[_tool_call('get_weather', {'city': 'Denver'})],
    )

    with pytest.raises(ValueError, match='Unknown tool requested: get_weather'):
        call_tools({'messages': [message]})

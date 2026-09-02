import json
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.state import AgentState
from app.config import settings

from app.tools.get_inventory import get_inventory
from app.tools.get_purchase_orders import get_purchase_orders
from app.tools.get_sales_orders import get_sales_orders
from app.tools.get_shipments import get_shipments
from app.tools.get_supplies import get_supplies

TOOLS: list[BaseTool] = [
    get_inventory,
    get_purchase_orders,
    get_sales_orders,
    get_shipments,
    get_supplies
]

MODEL = ChatOpenAI(
    model=settings.model_name,
    temperature=settings.model_temperature,
    max_completion_tokens=settings.model_max_tokens,
    api_key=settings.openai_api_key
).bind_tools(TOOLS)

def call_model(state: AgentState) -> dict[str, Any]:
    '''Send the current conversation to the LLM.'''

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state['messages']
    ]

    response = MODEL.invoke(messages)

    return {
        'messages': [response]
    }

def call_tools(state: AgentState) -> dict[str, Any]:
    '''Execute tools requested by the LLM.'''

    last_message = state['messages'][-1]

    tool_calls = getattr(last_message, 'tool_calls', [])
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']

        selected_tool = next(
            (candidate for candidate in TOOLS if candidate.name == tool_name),
            None
        )

        if selected_tool is None:
            raise ValueError(f'Unknown tool requested: {tool_name}')

        result = selected_tool.invoke(tool_args)

        results.append({
            'role': 'tool',
            'content': json.dumps(result, default=str),
            'tool_call_id': tool_call['id']
        })

    return {
        'messages': results
    }
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.state import AgentState
from app.agent.nodes import call_model, call_tools

def should_continue(state: AgentState) -> str:
    '''Determine whether the agent needs to execute a tool.'''

    last_message = state['messages'][-1]

    if getattr(last_message, 'tool_calls', None):
        return 'tools'

    return END

def build_graph() -> CompiledStateGraph:
    '''Build and compile the supply chain agent graph.'''

    graph = StateGraph(AgentState)

    graph.add_node('agent', call_model)
    graph.add_node('tools', call_tools)

    graph.add_edge(START, 'agent')
    graph.add_conditional_edges(
        'agent',
        should_continue,
        {
            'tools': 'tools',
            END: END
        }
    )
    graph.add_edge('tools', 'agent')

    return graph.compile(checkpointer=InMemorySaver())
    
agent = build_graph()
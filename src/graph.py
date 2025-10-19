from langgraph.graph import StateGraph, START, END, add_messages

from agent import planning_node, selenium_node, route_workflow_node, tool_node, State, summarize_node

def create_graph() -> StateGraph:
    graph = StateGraph(State)

    graph.add_node("planning", planning_node)
    graph.add_node("agent", selenium_node)
    graph.add_node("tools", tool_node)
    graph.add_node("summarize", summarize_node)

    graph.add_edge(START, "planning")
    graph.add_edge("planning", "agent")

    graph.add_conditional_edges(
        "agent",
        route_workflow_node,
        {
            "agent": "agent",
            "summarize": "summarize",
            "tools": "tools",
        }
    )

    graph.add_edge("tools", "agent")
    graph.add_edge("summarize", END)

    return graph.compile()
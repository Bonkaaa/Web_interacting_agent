# from langgraph.graph import StateGraph, START, END, add_messages

# from agent import planning_node, selenium_node, route_workflow_node, tool_node, State, summarize_node

# def create_graph() -> StateGraph:
#     graph = StateGraph(State)

#     graph.add_node("planner", planning_node)
#     graph.add_node("agent", selenium_node)
#     graph.add_node("tools", tool_node)
#     graph.add_node("summarize", summarize_node)

#     graph.add_edge(START, "planner")
#     graph.add_edge("planner", "agent")

#     graph.add_conditional_edges(
#         "agent",
#         route_workflow_node,
#         {
#             "agent": "agent",
#             "summarize": "summarize",
#             "tools": "tools",
#         }
#     )

#     graph.add_edge("tools", "agent")
#     graph.add_edge("summarize", END)

#     return graph.compile()

from langgraph.graph import StateGraph, START, END, add_messages
from agent import start_driver_and_access_url_node, extract_accessibility_tree_node, reAct_node, State, click_node, type_node, wait_node, go_home_node, go_back_node

def create_graph() -> StateGraph:
    graph = StateGraph(State)

    graph.add_node("start_driver_and_access_url", start_driver_and_access_url_node)
    graph.add_node("extract_accessibility_tree", extract_accessibility_tree_node)
    graph.add_node("reAct", reAct_node)
    graph.add_node("click", click_node)
    graph.add_node("type", type_node)
    graph.add_node("wait", wait_node)
    graph.add_node("go_home", go_home_node)
    graph.add_node("go_back", go_back_node)

    graph.add_edge(START, "start_driver_and_access_url")
    graph.add_edge("start_driver_and_access_url", "extract_accessibility_tree")
    graph.add_edge("extract_accessibility_tree", "reAct")
    # # graph.add_edge("reAct", "click")
    # graph.add_edge("click", END)

    # graph.add_edge("reAct", "type")
    # graph.add_edge("type", END)

    # graph.add_edge("reAct", "wait")
    # graph.add_edge("wait", END)

    # graph.add_edge("reAct", "go_home")
    # graph.add_edge("go_home", END)

    graph.add_edge("reAct", "go_back")
    graph.add_edge("go_back", END)

    return graph.compile()

if __name__ == "__main__":
    graph = create_graph()
    
    from IPython.display import display, Image

    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))   
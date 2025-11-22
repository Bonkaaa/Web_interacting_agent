from langgraph.graph import StateGraph, START, END, add_messages
from agent import start_driver_and_access_url_node, extract_accessibility_tree_node, reAct_node, State, click_node, type_node, wait_node, go_home_node, go_back_node, route_workflow_node, should_continue_node, extract_data_node

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
    graph.add_node("extract_data", extract_data_node)

    graph.add_edge(START, "start_driver_and_access_url")
    graph.add_edge("start_driver_and_access_url", "extract_accessibility_tree")
    graph.add_edge("extract_accessibility_tree", "reAct")
    
    graph.add_conditional_edges(
        "reAct",
        route_workflow_node,
        {
            "click": "click",
            "type": "type",
            "wait": "wait",
            "go_home": "go_home",
            "go_back": "go_back",
            "extract_data": "extract_data",
            "extract_accessibility_tree": "extract_accessibility_tree",
        }
    )

    graph.add_conditional_edges(
        "click",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    graph.add_conditional_edges(
        "type",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    graph.add_conditional_edges(
        "wait",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    graph.add_conditional_edges(
        "go_home",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    graph.add_conditional_edges(
        "go_back",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    graph.add_conditional_edges(
        "extract_data",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "END": END,
        }
    )

    return graph.compile()

if __name__ == "__main__":
    graph = create_graph()
    
    from IPython.display import display, Image

    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))   
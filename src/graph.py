from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Any, List, Union
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from selenium.webdriver.remote.webelement import WebElement
from agent import start_driver_and_access_url_node, extract_accessibility_tree_node, reAct_node, State, click_node, type_node, wait_node, go_home_node, go_back_node, route_workflow_node, should_continue_node, extract_data_node, answer_node

def create_graph() -> StateGraph:
    graph = StateGraph(State)

    # Nodes
    graph.add_node("start_driver_and_access_url", start_driver_and_access_url_node)
    graph.add_node("extract_accessibility_tree", extract_accessibility_tree_node)
    graph.add_node("reAct", reAct_node)

    # Action Nodes
    graph.add_node("click", click_node)
    graph.add_node("type", type_node)
    graph.add_node("wait", wait_node)
    graph.add_node("go_home", go_home_node)
    graph.add_node("go_back", go_back_node)
    graph.add_node("extract_data", extract_data_node)

    # Answer Node
    graph.add_node("answer", answer_node)

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
            "answer": "answer",
            "__default__": "answer",
        }
    )

    graph.add_conditional_edges(
        "click",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_conditional_edges(
        "type",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_conditional_edges(
        "wait",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_conditional_edges(
        "go_home",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_conditional_edges(
        "go_back",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_conditional_edges(
        "extract_data",
        should_continue_node,
        {
            "extract_accessibility_tree": "extract_accessibility_tree",
            "answer": "answer",
        }
    )

    graph.add_edge("answer", END)

    return graph.compile()

if __name__ == "__main__":
    class State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]
        task: str
        data_from_web_elements: List[str]
        web_element: WebElement
        url: str
        driver: object
        accessibility_tree_str: str
        accessibility_node_map: dict[str, Any]
        action_history: List[List[Union[str, str, str]]] # [role, name, action]
        warn_obs: List[str]
        action: List[Union[int, str]]
        tool_count: int = 0
        max_tool_usage: int = 3
        final_anwser: str

    initial_state: State = {
        "messages": [],
        # "task": "Click on the Terms link at the bottom of the page", # FOR CLICK TESTING
        # "task": "Type 'Hello, Chatgpt' into the text box", # FOR TYPE TESTING
        # "task": "Wait for 5 seconds", # FOR WAIT TESTING
        # "task": "Go to the home page", # FOR GO HOME TESTING
        "task": "Find the terms link and find out when the terms are published", # FOR REAL TESTING
        "data_from_web_elements": [],
        "web_element": None,
        "url": "https://chatgpt.com",
        "driver": None,
        "accessbility_tree_str": "",
        "accessbility_node_map": {},
        "action_history": [],
        "warn_obs": [],
        "action": [], 
        "tool_count": 0,
        "max_tool_usage": 3,
        "final_anwser": "",       
    }

    graph = create_graph()
    final_state = graph.invoke(initial_state)
    print("Final Answer:", final_state["final_anwser"])
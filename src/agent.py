from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage

from selenium.webdriver.remote.webelement import WebElement

from utils import setup_logger
from tools import create_webdriver, access_url, extract_accessibility_tree, parse_accessibility_tree, extract_element_from_accessibility_tree, execute_click_action, execute_type_action, execute_wait_action, execute_go_home_action, execute_go_back_action, extract_data_from_element

from components.reAct import reAct_agent
from components.answer import create_answer_agent
from components.check_cont import create_check_continue_agent

from typing_extensions import TypedDict, Annotated, Any, List, Union
import json

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

logger = setup_logger("new_agent")

def start_driver_and_access_url_node(state: State) -> dict:
    try:
        driver_response = create_webdriver()

        access_url(driver_response, state["url"])
        logger.info(f"Accessed URL: {state['url']}")
    except Exception as e:
        logger.error(f"Error in start_driver_and_access_url: {e}")
    return {
        "driver": driver_response,
    }

def extract_accessibility_tree_node(state: State) -> dict:
    webdriver = state["driver"]

    if webdriver:
        accessibility_tree = extract_accessibility_tree(webdriver)
        accessibility_tree_str, accessibility_node_map = parse_accessibility_tree(accessibility_tree)

        if accessibility_tree_str and accessibility_node_map:
            logger.info("Extracted and parsed accessibility tree successfully.")
        else:
            logger.error("Failed to parse accessibility tree.")
    else:
        logger.error("WebDriver instance is not available.")
        return {}

    return {
        "accessibility_tree_str": accessibility_tree_str,
        "accessibility_node_map": accessibility_node_map
    }

def reAct_node(state: State) -> dict:
    reAct = reAct_agent()

    user_message = f"""
    Message for ReAct Agent:
    Task: {state['task']}
    Accessibility Tree: {state['accessibility_tree_str']}
    Action History: {json.dumps(state['action_history'])}
    """

    human_message = HumanMessage(content=user_message)
    
    new_messages = [human_message]

    reAct_input = {
        "accessibility_tree_str": state["accessibility_tree_str"],
        "action_history": json.dumps(state["action_history"]),
        "task": state["task"]
    }

    try:
        reAct_response = reAct.invoke(reAct_input)

        thought = reAct_response.thought
        action = reAct_response.action

        logger.info(f"ReAct Thought: {thought}")
        logger.info(f"ReAct Action: {action}")


        ai_message = AIMessage(content=f"Thought: {thought}\nAction: {action}")
        new_messages.append(ai_message)

        return {
            "messages": new_messages,
            "action": action
        }

    except Exception as e:
        logger.error(f"Error in reAct_node: {e}")
        return {
            "messages": new_messages,
            "action": []
        }

def click_node(
    state: State
) -> dict:
    driver = state["driver"]
    accessibility_node_map = state["accessibility_node_map"]
    action = state["action"]

    if not driver or not accessibility_node_map or not action:
        error = "Missing driver, accessibility_node_map, or action in state."
        logger.error(error)
        return {
            "warn_obs": error
        }

    element_index = action[0]
    action_type = action[1]

    if "click" not in action_type.lower():
        error = f"Action type is not click: {action_type}"
        logger.error(error)
        return {
            "warn_obs": error
        }
        
    web_element, role, name = extract_element_from_accessibility_tree(
        node_idx=element_index,
        node_map=accessibility_node_map,
        driver=driver
    )

    if not web_element:
        error = f"Web element not found for index: {element_index}"
        logger.error(error)
        return {
            "warn_obs": error
        }
        
    try:
        execute_click_action(
            driver=driver,
            web_element=web_element
        )
        logger.info(f"Executed click action on element index: {element_index}")
        return {
            "warn_obs": "",
            "action_history": state["action_history"] + [[role, name, "click"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error executing click action: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }

### NEED DEBUGGING
def type_node(state: State) -> dict:
    driver = state["driver"]
    accessibility_node_map = state["accessibility_node_map"]
    action = state["action"]

    if not driver or not accessibility_node_map or not action:
        error = "Missing driver, accessibility_node_map, or action in state."
        logger.error(error)
        return {
            "warn_obs": error
        }

    element_index = action[0]
    action_type = action[1]
    text_to_type = action[2] if len(action) > 2 else ""

    if "type" not in action_type.lower():
        error = f"Action type is not type: {action_type}"
        logger.error(error)
        return {
            "warn_obs": error
        }
        
    web_element, role, name = extract_element_from_accessibility_tree(
        node_idx=element_index,
        node_map=accessibility_node_map,
        driver=driver
    )

    if not web_element:
        error = f"Web element not found for index: {element_index}"
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    try:
        execute_type_action(
            driver=driver,
            web_element=web_element,
            text=text_to_type
        )
        logger.info(f"Executed type action on element index: {element_index}")
        return {
            "warn_obs": "",
            "action_history": state["action_history"] + [[role, name, f"Type {text_to_type}"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error executing type action: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }

        
def wait_node(state: State) -> dict:
    driver = state["driver"]

    if not driver:
        error = "Missing driver in state."
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    try:
        execute_wait_action(driver=driver)
        logger.info("Executed wait action.")
        return {
            "warn_obs": "",
            "action_history": state["action_history"] + [["N/A", "N/A", "wait"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error executing wait action: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }

def go_home_node(state: State) -> dict:
    driver = state["driver"]

    if not driver:
        error = "Missing driver in state."
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    try:
        execute_go_home_action(driver=driver)
        logger.info("Executed go home action.")
        return {
            "warn_obs": "",
            "action_history": state["action_history"] + [["N/A", "N/A", "go_home"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error executing go home action: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }

def go_back_node(state: State) -> dict:
    driver = state["driver"]

    if not driver:
        error = "Missing driver in state."
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    try:
        execute_go_back_action(driver=driver)
        logger.info("Executed go back action.")
        return {
            "warn_obs": "",
            "action_history": state["action_history"] + [["N/A", "N/A", "go_back"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error executing go back action: {e}"
        logger.error(error)
        return {     
            "warn_obs": error
        }

def extract_data_node(state: State) -> dict:
    driver = state["driver"]
    accessibility_node_map = state["accessibility_node_map"]
    action = state["action"]

    if not driver or not accessibility_node_map or not action:
        error = "Missing driver, accessibility_node_map, or action in state."
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    element_index = action[0]
    action_type = action[1]

    if "extract" not in action_type.lower():
        error = f"Action type is not extract: {action_type}"
        logger.error(error)
        return {
            "warn_obs": error
        }

    web_element, role, name = extract_element_from_accessibility_tree(
        node_idx=element_index,
        node_map=accessibility_node_map,
        driver=driver
    )

    if not web_element:
        error = f"Web element not found for index: {element_index}"
        logger.error(error)
        return {
            "warn_obs": error
        }
    
    try:
        extracted_data = extract_data_from_element(web_element=web_element)
        logger.info(f"Extracted data from element index: {element_index}")
        return {
            "warn_obs": "",
            "data_from_web_elements": state["data_from_web_elements"] + [extracted_data],
            "action_history": state["action_history"] + [[role, name, "extract"]],
            "tool_count": state["tool_count"] + 1
        }
    except Exception as e:
        error = f"Error extracting data from element: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }
    
def route_workflow_node(state: State): 
    action = state.get("action", [])

    if not action or len(action) < 2:
        logger.warning("No valid action found. Routing back to agent.")
        return "extract_accessibility_tree"
    
    action_type = action[1].lower()

    if "click" in action_type:
        return "click"
    elif "type" in action_type:
        return "type"
    elif "wait" in action_type:
        return "wait"
    elif "go_home" in action_type:
        return "go_home"
    elif "go_back" in action_type:
        return "go_back"
    elif "extract" in action_type:
        return "extract_data"
    else:
        logger.warning(f"Unknown action type: {action_type}. Routing back to agent.")
        return "extract_accessibility_tree"
    
def should_continue_node(state: State) -> dict:
    tool_count = state.get("tool_count", 0)
    max_tool_usage = state.get("max_tool_usage", 10)

    if tool_count >= max_tool_usage:
        logger.info(f"Reached maximum tool usage: {tool_count}/{max_tool_usage}. Routing to summarize node.")
        return "anwser"
    else:
        logger.info(f"Tool usage: {tool_count}/{max_tool_usage}. Invoking Check Continue Agent.")
        check_continue = create_check_continue_agent()
        user_message = f"""
        Message for Check Continue Agent:
        Task: {state['task']}
        Extracted Information: {json.dumps(state['data_from_web_elements'])}
        Accessibility Tree: {state['accessibility_tree_str']}
        """

        human_message = HumanMessage(content=user_message)

        new_messages = [human_message]

        check_continue_input = {
            'extracted_info': json.dumps(state["data_from_web_elements"]),
            'accessibility_tree_str': state["accessibility_tree_str"],
            'task': state["task"]
        }

        try:
            check_continue_response = check_continue.invoke(check_continue_input)

            decision = check_continue_response.decision

            logger.info(f"Decision for continue or stop using web interaction: {decision}")

            ai_message = AIMessage(content=f'Decision: {decision}')
            new_messages.append(ai_message)

        except Exception as e:
            logger.error(f"Error in should_continue_node: {e}")
            decision = "CONTINUE"

        if "FINAL ANSWER" in decision.upper():
            return "answer"
        else:
            return "extract_accessibility_tree"
    
def answer_node(state: State):
    answer = create_answer_agent()

    user_message = f"""
    Message for Answer Agent:
    Task: {state['task']}
    Extracted Information: {json.dumps(state['data_from_web_elements'])}
    Accessibility Tree: {state['accessibility_tree_str']}
    """

    human_message = HumanMessage(content=user_message)

    new_messages = [human_message]
    answer_input = {
        "extracted_info": json.dumps(state["data_from_web_elements"]),
        "accessibility_tree_str": state["accessibility_tree_str"],
        "task": state["task"]
    }

    try:
        answer_response = answer.invoke(answer_input)

        final_answer = answer_response.answer

        logger.info(f"Final Answer: {final_answer}")

        ai_message = AIMessage(content=f"Final Answer: {final_answer}")
        new_messages.append(ai_message)

        return {
            "messages": new_messages,
            "final_anwser": final_answer
        }
    except Exception as e:
        logger.error(f"Error in answer_node: {e}")
        return {
            "messages": new_messages,
            "final_anwser": ""
        }


    







            

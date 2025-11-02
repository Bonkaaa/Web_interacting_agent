from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage

from selenium.webdriver.remote.webelement import WebElement

from utils import setup_logger
from tools import create_webdriver, access_url, extract_accessibility_tree, parse_accessibility_tree, extract_element_from_accessibility_tree, execute_click_action, execute_type_action, execute_wait_action, execute_go_home_action, execute_go_back_action, extract_data_from_element

from components.reAct import reAct_agent

from typing_extensions import TypedDict, Annotated, Any, List, Union
import json

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    task: str
    answer: str
    web_element: WebElement
    url: str
    driver: object
    accessibility_tree_str: str
    accessibility_node_map: dict[str, Any]
    action_history: List[List[Union[str, str, str]]] # [role, name, action]
    warn_obs: List[str]
    action: List[Union[int, str]]

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
    logger.info(f"ReAct User Message: {human_message.content}")
    
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
            "action_history": state["action_history"] + [[role, name, "click"]]
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
            "action_history": state["action_history"] + [[role, name, f"Type {text_to_type}"]]
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
            "action_history": state["action_history"] + [["N/A", "N/A", "wait"]]
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
            "action_history": state["action_history"] + [["N/A", "N/A", "go_home"]]
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
            "action_history": state["action_history"] + [["N/A", "N/A", "go_back"]]
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
            "answer": extracted_data,
            "action_history": state["action_history"] + [[role, name, "extract"]]
        }
    except Exception as e:
        error = f"Error extracting data from element: {e}"
        logger.error(error)
        return {
            "warn_obs": error
        }





            

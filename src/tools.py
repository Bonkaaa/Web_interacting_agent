from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from utils import setup_logger
import time
import random

from typing import Any, TypedDict, Literal

logger = setup_logger("tools")
IndentStyle = Literal["ASCII", "Tab"]

class AccessibilityTreeNode(TypedDict):
    nodeId: str
    ignored: bool
    role: dict[str, Any]
    chromeRole: dict[str, Any]
    name: dict[str, Any]
    properties: list[dict[str, Any]]
    childIds: list[str]
    parentId: str
    backendDOMNodeId: str
    frameId: str

AccessibilityTree = list[AccessibilityTreeNode]


def create_webdriver() -> webdriver.Chrome:
    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    logger.info("WebDriver instance created.")
    return driver

def access_url(driver: webdriver.Chrome, url: str) -> None:
    driver.get(url)
    logger.info(f"Accessed URL: {url}")


def extract_accessibility_tree(
    driver
) -> AccessibilityTree:
    try:
        result = driver.execute_cdp_cmd("Accessibility.getFullAXTree", {})
        nodes = result.get("nodes", [])

        seen_ids = set()
        unique_nodes = []
        for node in nodes:
            if node["nodeId"] not in seen_ids:
                unique_nodes.append(node)
                seen_ids.add(node["nodeId"])

        return unique_nodes
    except Exception as e:
        logger.info(f"Error extracting accessibility tree: {e}")
        return []
    
def parse_accessibility_tree(
    accessibility_tree: AccessibilityTree,
    max_node: int = 300,
    indent_style: IndentStyle = "Tab"
) -> tuple[str, dict[str, Any]]:
    """
    Parse the accessibility tree to extract text content and a summary of elements.
    Args:
        accessibility_tree (AccessibilityTree): The accessibility tree to parse.
    Returns:
        tuple[str, list[dict[str, Any]]]: Extracted text content and a summary of elements.
    """
    indent_map = {
        "ASCII": "│   ",
        "Tab": "\t"
    }

    indent_str = indent_map[indent_style]

    node_id_to_idx = {}

    tree_list = []

    for idx, node in enumerate(accessibility_tree):
        node_id_to_idx[node['nodeId']] = idx

    node_map = {}
    def dfs(node_id, depth=0, parent_node='root'):
        valid_node = True

        indent = indent_str * depth

        if len(node_map) > max_node:
            return
        
        node = accessibility_tree[node_id_to_idx[node_id]]
        
        try:
            role = node.get('role', {}).get('value', '')
            name = node.get('name', {}).get('value', '')

            if not name.strip() or role in ['gridcell'] or (name.strip() in parent_node and role in ['StaticText', 'heading', 'image', 'generic']):
                valid_node = False
        
            if valid_node:
                idx = len(node_map) + 1
                node_map[idx] = node
                if IndentStyle == "ASCII":
                    tree_list.append(f"{indent}├── [{idx}] {role} '{name}'")
                else:
                    tree_list.append(f"{indent} [{idx}] {role} '{name}'")
        except Exception as e:
            valid_node = False

        for child_id in node.get('childIds', []):
            if child_id not in node_id_to_idx:
                continue
            child_depth = depth + 1 if valid_node else depth
            curr_name = name if valid_node else parent_node
            dfs(child_id, child_depth, parent_node=curr_name)

    dfs(accessibility_tree[0]['nodeId'])
    tree_str = "\n".join(tree_list)
    return tree_str, node_map

def extract_element_from_accessibility_tree(
    node_idx: int,
    node_map: dict[str, Any],
    driver: webdriver.Chrome
) -> tuple[Any, str, str] | None:
    backend_DOM_node_id = node_map[node_idx]['backendDOMNodeId']

    role = node_map[node_idx].get('role', {}).get('value', '')
    name = node_map[node_idx].get('name', {}).get('value', '')

    obj = driver.execute_cdp_cmd(
        "DOM.resolveNode",
        {
            "backendNodeId": backend_DOM_node_id
        }
    )

    object_id = obj['object']['objectId']

    tag_id = random.randint(100000, 999999)
    tag_atribute = f"web_interacting_agent_tag_{tag_id}"

    driver.execute_cdp_cmd(
        "Runtime.callFunctionOn",
        {
            "functionDeclaration": f"function() {{ this.setAttribute('{tag_atribute}', 'true'); }}",
            "objectId": object_id,
        }
    )

    selector = f"[{tag_atribute}='true']"

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
    except TimeoutException:
        logger.error("Timed out waiting for the web element to be located.")
        return None
    
    element = driver.find_element(By.CSS_SELECTOR, selector)
    
    driver.execute_cdp_cmd(
        "Runtime.callFunctionOn",
        {
            "functionDeclaration": f"function() {{ this.removeAttribute('{tag_atribute}'); }}",
            "objectId": object_id,
        }
    )

    return element, role, name

def execute_click_action(
    driver: webdriver.Chrome,
    web_element: Any
) -> None:
    original_tabs = driver.window_handles
    driver.execute_script("arguments[0].setAttribute('target', '_self');", web_element)
    web_element.click()
    time.sleep(3)
    new_tabs = driver.window_handles
    if len(new_tabs) > len(original_tabs):
        new_tab = [tab for tab in new_tabs if tab not in original_tabs][0]
        driver.switch_to.window(new_tab)
        new_tab_url = driver.current_url
        driver.close()
        driver.switch_to.window(original_tabs[0])
        driver.get(new_tab_url)
        time.sleep(2)

def execute_type_action(
    driver: webdriver.Chrome,
    web_element: Any,
    text: str
) -> str:
    warn_obs = ""

    element_tag_name = web_element.tag_name.lower()
    element_type = web_element.get_attribute("type") or ""

    if element_tag_name != "input" and element_type != "textarea":
        warn_obs = f"Warning: The web element you are trying to type into may not be a textbox. It is a <{element_tag_name}> element, type '{element_type}'."
        logger.warning(warn_obs)

    # Clear existing text
    try:
        web_element.clear()
        web_element.send_keys(" ")
        web_element.send_keys(Keys.BACKSPACE)
    except:
        logger.warning("Unable to clear existing text in the web element.")

    action = ActionChains(driver)

    action.click(web_element).perform()
    time.sleep(1)

    action.send_keys(text).perform()
    time.sleep(2)

    action.send_keys(Keys.ENTER).perform()
    time.sleep(5)

    return warn_obs

def execute_wait_action(
    driver: webdriver.Chrome,
) -> None:
    time.sleep(5)

def execute_go_back_action(
    driver: webdriver.Chrome,
) -> None:
    driver.back()
    time.sleep(5)

def execute_go_home_action(
    driver: webdriver.Chrome,
) -> None:
    driver.get('https://www.google.com')
    time.sleep(5)

def extract_data_from_element(
    web_element: WebElement
) -> str:
    try:
        text_content = web_element.text
        return text_content
    except Exception as e:
        logger.error(f"Error extracting text from web element: {e}")
        return ""
    
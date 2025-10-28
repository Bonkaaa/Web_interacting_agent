from .utils import setup_logger, dump_json_to_file
from typing import Any, TypedDict 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import json



logger = setup_logger("utils_agent")

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
    max_depth: int = 5,
    max_node: int = 300
) -> tuple[str, dict[str, Any]]:
    """
    Parse the accessibility tree to extract text content and a summary of elements.
    Args:
        accessibility_tree (AccessibilityTree): The accessibility tree to parse.
    Returns:
        tuple[str, list[dict[str, Any]]]: Extracted text content and a summary of elements.
    """
    node_id_to_idx = {}

    tree_list = []

    for idx, node in enumerate(accessibility_tree):
        node_id_to_idx[node['nodeId']] = idx

    node_map = {}
    def dfs(node_id, depth=0, parent_node='root'):
        valid_node = True

        if depth > max_depth or len(node_map) > max_node:
            return
        
        node = accessibility_tree[node_id_to_idx[node_id]]
        
        try:
            role = node.get('role', {}).get('value', '')
            name = node.get('name', {}).get('value', '')

            if not name.strip() or role in ['gridcell']:
                valid_node = False
        
            if valid_node:
                idx = len(node_map) + 1
                node_map[idx] = node
                tree_list.append(f"{'\t' * depth} [{idx}] {role} '{name}'")
        except Exception as e:
            valid_node = False

        for child_id in node.get('childIds', []):
            if child_id not in node_id_to_idx:
                continue
            depth += 1 if valid_node else depth
            dfs(child_id, depth, parent_node=name)

    dfs(accessibility_tree[0]['nodeId'])
    breakpoint()
    tree_str = "\n".join(tree_list)
    return tree_str, node_map

if __name__ == "__main__":
    options = Options()

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://chatgpt.com")

    accessibility_tree = extract_accessibility_tree(driver)

    tree_str, node_map = parse_accessibility_tree(accessibility_tree)
    dump_json_to_file(accessibility_tree, "accessibility_tree.json")

    dump_json_to_file(node_map, "parsed_accessibility_tree.json")

    print(tree_str)
    print(f"Total nodes extracted: {len(node_map)}")

        
            





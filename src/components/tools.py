from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import time
import random

from langchain_core.tools import tool

from bs4 import BeautifulSoup as BS

from utils import setup_logger

logger = setup_logger("tools")

_driver = None

@tool
def create_driver():
    """
    Create and return a Selenium WebDriver instance.
    """
    global _driver
    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    _driver = webdriver.Chrome(service=service, options = options)

    logger.info("WebDriver instance created.")
    return {"message": "WebDriver instance created."}

@tool
def access_url(url: str):
    """
    Tool to access a URL
    Args:
        url (str): The URL to access.

    Example: access_url("http://bing.com")
    """
    global _driver
    if _driver is None:
        return "Error: No driver created. Please create a driver first."

    _driver.get(url)
    logger.info(f"Accessed URL: {url}")

@tool
def find_element(by: str, value: str):
    """
    Tool to find an element by a given method
    Args:
        by (str): The method to locate the element (e.g., "name", "id", "xpath").
        value (str): The value to locate the element.
        driver: The Selenium WebDriver instance.
    Returns:
        WebElement or str: The found element or a message indicating it was not found.

    Example: find_element("name", "q")
    """

    global _driver
    if _driver is None:
        logger.error("No driver created. Please create a driver first.")
        return "Error: No driver created. Please create a driver first."


    by_methods = {
        "name": By.NAME,
        "id": By.ID,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }
    if by not in by_methods:
        logger.error(f"Invalid 'by' method: {by}. Choose from {list(by_methods.keys())}.")
        return f"Invalid 'by' method: {by}. Choose from {list(by_methods.keys())}."
    
    try:
        element = WebDriverWait(_driver, 10).until(
            EC.presence_of_element_located((by_methods[by], value))
        )
        logger.info(f"Element found by {by} with value {value}.")
        return element
    except TimeoutException:
        logger.error(f"Element not found by {by} with value {value}.")
        return f"Element not found by {by} with value {value}."

@tool  
def click_element(by: str, value: str):
    """
    Tool to click on a web element found by a given method.
    Args:
        by (str): The method to locate the element (e.g., "name", "id", "xpath").
        value (str): The value to locate the element.
    Returns:
        str: A message indicating the result of the click action.

    Example: click_element("id", "submit-button")
    """

    global _driver
    if _driver is None:
        return "Error: No driver created. Please create a driver first."

    by_mapping = {
        "name": By.NAME,
        "id": By.ID,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }

    if by not in by_mapping:
        logger.error(f"Invalid 'by' method: {by}. Choose from {list(by_mapping.keys())}.")
        return f"Invalid 'by' method: {by}. Choose from {list(by_mapping.keys())}."
    
    try:
        element = _driver.find_element(by_mapping[by], value)
        element.click()
        logger.info(f"Clicked element found by {by} with value {value}.")
        return f"Clicked element found by {by} with value {value}."
    except Exception as e:
        logger.error(f"Error clicking element: {e}")
        return f"Error clicking element: {e}"

@tool
def search_element(by: str, value: str, query: str):
    """
    Tool to input a search query into a web element and press Enter.
    Args:
        by (str): The method to locate the element (e.g., "name", "id", "xpath").
        value (str): The value to locate the element.
        query (str): The search query to input.
    Returns:
        str: A message indicating the result of the search action.

    Example: search_element("name", "q", "Latest news on AI")
    """
    
    global _driver
    if _driver is None:
        return "Error: No driver created. Please create a driver first."
    
    by_mapping = {
        "name": By.NAME,
        "id": By.ID,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT
    }

    if by not in by_mapping:
        logger.error(f"Invalid 'by' method: {by}. Choose from {list(by_mapping.keys())}.")
        return f"Invalid 'by' method: {by}. Choose from {list(by_mapping.keys())}."
    
    try:
        element = _driver.find_element(by_mapping[by], value)
        element.clear()
        for char in query:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(Keys.ENTER)
        logger.info(f"Searched '{query}' in element found by {by} with value {value}.")
        return f"Searched '{query}' in element found by {by} with value {value}."
    except Exception as e:
        logger.error(f"Error searching element: {e}")
        return f"Error searching element: {e}"
    
@tool
def simplify_html():
    """
    Tool to extract HTML and simplify the HTML content of the current page.
    Returns:
        list[dict]: A simplified representation of the HTML content.
    """
    html = _driver.page_source

    html_content = BS(html, 'html.parser')

    summary = []

    for tag in html_content(['script', 'style', 'meta', 'link']):
        tag.decompose()

    for element in html_content.find_all(['button', 'input', 'select', 'textarea', 'a', 'form', 'details', 'summary', 'dialog', 'label']):
        element_info = {
            'tag': element.name,
            'text': element.get_text(strip=True)[:100],  # Limit text length
            'id': element.get('id'),
            'class': element.get('class'),
            'name': element.get('name'),
            'type': element.get('type'),
        }
        summary.append(element_info)

    return summary

@tool
def extract_content_from_html():
    """
    Helper function to extract and simplify HTML content.
    Returns:
        list[dict]: A simplified representation of the HTML content.
    """

    html = _driver.page_source

    html_content = BS(html, 'html.parser')

    summary = []

    for tag in html_content(['script', 'style', 'meta', 'link']):
        tag.decompose()

    for element in html_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div']):
        element_info = {
            'tag': element.name,
            'content': element.get_text(strip=True)[:200],  # Limit text length
            'id': element.get('id'),
            'class': element.get('class'),
        }
        summary.append(element_info)

    return summary
    

@tool
def close_driver():
    """
    Tool to close the Selenium WebDriver instance.
    """
    global _driver
    if _driver:
        _driver.quit()
        _driver = None
        logger.info("WebDriver instance closed.")

tools = [
    create_driver,
    access_url,
    find_element,
    click_element,
    search_element,
    simplify_html,
    extract_content_from_html,
    close_driver,
]


if __name__ == "__main__":
    create_driver()
    print(type(_driver))
    breakpoint()
    # Open the homepage
    access_url("http://bing.com")

    time.sleep(2)

    # time.sleep(2)
    
    # Test the search box
    # search_box = find_element("id", "search", driver)

    # search_element(search_box, "Hello world Python programming")

    # time.sleep(2)

    # button_element = find_element("tag", "button", driver)
    # click_element(button_element)

    # time.sleep(2)

    # html = get_html_from_driver()

    # simplified = simplify_html(html)

    # dump_json_to_file(simplified, "simplified_html.json")

    search_box = find_element("name", "q")
    search_element("name", "q", "Latest news on AI")
    time.sleep(5)

    





    
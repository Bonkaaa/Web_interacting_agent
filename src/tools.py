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

from langchain_core.tools import Tool

from bs4 import BeautifulSoup as BS

from .utils import write_text_to_file, dump_json_to_file, setup_logger

logger = setup_logger("tools")



# def interact_with_website_to_get_to_the_first_link(url, search_query, action="click", wait_time=10):
#     """
#     Interact with a website using Selenium WebDriver.
#     Args:
#         url (str): The URL of the website to interact with.
#         search_query (str): The search query to input.
#         action (str): The action to perform ("click" or "get_text").
#         wait_time (int): Maximum wait time for elements to load.
#     Returns:
#         str: The text content of the first link found on the page or a message indicating no link was found.
#     """
    
#     options = Options()
#     # options.add_argument("--headless")
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options = options)

#     driver.get(url)
#     WebDriverWait(driver, wait_time).until(
#         EC.presence_of_element_located((By.NAME, "q"))
#     )

#     search_box = driver.find_element(By.NAME, "q")
#     for char in search_query:
#         search_box.send_keys(char)
#         time.sleep(random.uniform(0.1, 0.3))
#     search_box.send_keys(Keys.ENTER)

#     time.sleep(5)

#     current_url = driver.current_url

#     if "captcha" in current_url.lower() or "sorry" in current_url.lower():
#         print("Captcha detected! Please solve it manually...")
#         input("Press Enter after solving the captcha to continue...")
#     else:
#         print("Search completed successfully!")

#     try: 
#         titles = driver.find_elements(By.TAG_NAME, "h3")
#         print(f"\nFound {len(titles)} search result titles:")
#         for i, title in enumerate(titles[:5], 1):  # Show first 5 results
#             if title.text:
#                 print(f"{i}. {title.text}")
#     except Exception as e:
#         print(f"Error extracting titles: {e}")

#     search_query = search_query.split(" ")

#     for letter in search_query:
#         try:
#             WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, letter))
#             )
#             link = driver.find_element(By.PARTIAL_LINK_TEXT, letter)
#             link.click()
#             break
#         except TimeoutException:
#             print("Element not found, continuing...")

#     time.sleep(5)

#     WebDriverWait(driver, wait_time).until(
#         EC.presence_of_element_located((By.TAG_NAME, "article"))
#     )

#     html = driver.page_source
#     soup = BS(html, "html.parser")

#     content_for_llm = {}

#     article = soup.find("article") if soup.find("article") else None
#     if article:
#         content_for_llm["article"] = article.get_text(separator="\n", strip=True)
    
#     main = soup.find("main") if soup.find("main") else None
#     if main:
#         content_for_llm["main"] = main.get_text(separator="\n", strip=True)
    
#     content_div = None
#     for id_name in ["content", "post", "article"]:
#         content_div = soup.find("div", id=id_name) if soup.find("div", id=id_name) else None
#         if content_div:
#             content_for_llm["content_div"] = content_div.get_text(separator="\n", strip=True)
#             break
    
#     paragraphs = soup.find_all("p") if soup.find_all("p") else []
#     if paragraphs:
#         para_texts = [p.get_text(separator="\n", strip=True) for p in paragraphs if p.get_text(strip=True)]
#         content_for_llm["paragraphs"] = "\n".join(para_texts)
    
#     headers = []
#     for level in range(1, 7):
#         headers.extend(soup.find_all(f"h{level}"))
#         if headers:
#             header_texts = [h.get_text(separator="\n", strip=True) for h in headers if h.get_text(strip=True)]
#             content_for_llm["headers"] = "\n".join(header_texts)
#             break

#     driver.quit()

#     return content_for_llm

def create_driver():
    """
    Create and return a Selenium WebDriver instance.
    Returns:
        WebDriver: The Selenium WebDriver instance.
    """
    options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options = options)
    return driver


def access_url(url: str, driver):
    """
    Tool to access a URL
    Args:
        url (str): The URL to access.
        driver: The Selenium WebDriver instance.
    Returns:
        str: A message indicating the URL was accessed.
    """
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    logger.info(f"Accessed URL: {url}")
    return f"Accessed URL: {url}"


def find_element(by: str, value: str, driver):
    """
    Tool to find an element by a given method
    Args:
        by (str): The method to locate the element (e.g., "name", "id", "xpath").
        value (str): The value to locate the element.
        driver: The Selenium WebDriver instance.
    Returns:
        WebElement or str: The found element or a message indicating it was not found.
    """
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
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_methods[by], value))
        )
        logger.info(f"Element found by {by} with value {value}.")
        return element
    except TimeoutException:
        logger.error(f"Element not found by {by} with value {value}.")
        return f"Element not found by {by} with value {value}."
    
def click_element(element):
    """
    Tool to click on a given web element.
    Args:
        element: The web element to click.
    Returns:
        str: A message indicating the result of the click action.
    """
    try:
        element.click()
        logger.info("Element clicked successfully.")
        return "Element clicked successfully."
    except Exception as e:
        logger.error(f"Error clicking element: {e}")
        return f"Error clicking element: {e}"

def search_element(element, query):
    """
    Tool to input a search query into a given web element.
    Args:
        element: The web element to input the query into.
        query (str): The search query to input.
    Returns:
        str: A message indicating the result of the input action.
    """
    try:
        for char in query:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        element.send_keys(Keys.ENTER)
        logger.info(f"Search query '{query}' input successfully.")
        return f"Search query '{query}' input successfully."
    except Exception as e:
        logger.error(f"Error inputting search query: {e}")
        return f"Error inputting search query: {e}"
    
def get_html_from_driver(driver):
    """
    Tool to get the HTML content from the current page of the WebDriver.
    Args:
        driver: The Selenium WebDriver instance.
    Returns:
        str: The HTML content of the current page.
    """
    try: 
        html = driver.page_source
        logger.info("HTML content retrieved successfully.")
        return html
    except Exception as e:
        logger.error(f"Error retrieving HTML content: {e}")
        return f"Error retrieving HTML content: {e}"
    
def simplify_html(html):
    """
    Tool to simplify HTML content by removing scripts, styles, and extracting key elements.
    Args:
        html (str): The HTML content to simplify.
    Returns:
        list: A summary of key HTML elements.
    """
    html_content = BS(html, 'html.parser')

    summary = []

    for tag in html_content(['script', 'style', 'meta', 'link']):
        tag.decompose()

    for element in html_content.find_all(['button', 'input', 'select', 'textarea', 'a', 'form']):
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

tools = [
    Tool(
        name="access_url",
        func=access_url,
        description="Access a URL to start interacting with a website. Input should be a valid URL string.",
        return_direct=True
    ),
    Tool(
        name="find_element",
        func=find_element,
        description="Find an element on the webpage by a given method (e.g., 'name', 'id', 'xpath'). Input should be a dictionary with 'by' and 'value' keys.",
        return_direct=True
    ),
    Tool(
        name="click_element",
        func=click_element,
        description="Click on a given web element. Input should be the web element to click.",
        return_direct=True
    ),
    Tool(
        name="search_element",
        func=search_element,
        description="Input a search query into a given web element. Input should be a dictionary with 'element' and 'query' keys.",
        return_direct=True
    ),
    Tool(
        name="get_html_from_driver",
        func=get_html_from_driver,
        description="Get the HTML content from the current page of the WebDriver. Input should be the WebDriver instance.",
        return_direct=True
    ),
    Tool(
        name="simplify_html",
        func=simplify_html,
        description="Simplify HTML content by removing scripts, styles, and extracting key elements. Input should be a string containing the HTML content.",
        return_direct=True
    ),
]




    



        

if __name__ == "__main__":
    driver = create_driver()
    access_url("https://www.google.com", driver)
    search_box = find_element("name", "q", driver)
    if "Element not found" not in str(search_box):
        search_element(search_box, "OpenAI")
        time.sleep(5)
        html = get_html_from_driver(driver)
        write_text_to_file("output.html", html)
        dump_json_to_file("output.json", {"html": html})
    driver.quit()
    
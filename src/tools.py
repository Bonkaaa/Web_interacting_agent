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

from .utils import write_text_to_file, dump_json_to_file


def interact_with_website_to_get_to_the_first_link(url, search_query, action="click", wait_time=10):
    """
    Interact with a website using Selenium WebDriver.
    Args:
        url (str): The URL of the website to interact with.
        search_query (str): The search query to input.
        action (str): The action to perform ("click" or "get_text").
        wait_time (int): Maximum wait time for elements to load.
    Returns:
        str: The text content of the first link found on the page or a message indicating no link was found.
    """
    
    options = Options()
    # options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options = options)

    driver.get(url)
    WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )

    search_box = driver.find_element(By.NAME, "q")
    for char in search_query:
        search_box.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
    search_box.send_keys(Keys.ENTER)

    time.sleep(5)

    current_url = driver.current_url

    if "captcha" in current_url.lower() or "sorry" in current_url.lower():
        print("Captcha detected! Please solve it manually...")
        input("Press Enter after solving the captcha to continue...")
    else:
        print("Search completed successfully!")

    try: 
        titles = driver.find_elements(By.TAG_NAME, "h3")
        print(f"\nFound {len(titles)} search result titles:")
        for i, title in enumerate(titles[:5], 1):  # Show first 5 results
            if title.text:
                print(f"{i}. {title.text}")
    except Exception as e:
        print(f"Error extracting titles: {e}")

    search_query = search_query.split(" ")

    for letter in search_query:
        try:
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, letter))
            )
            link = driver.find_element(By.PARTIAL_LINK_TEXT, letter)
            link.click()
            break
        except TimeoutException:
            print("Element not found, continuing...")

    time.sleep(5)

    WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.TAG_NAME, "article"))
    )

    html = driver.page_source
    soup = BS(html, "html.parser")

    content_for_llm = {}

    article = soup.find("article") if soup.find("article") else None
    if article:
        content_for_llm["article"] = article.get_text(separator="\n", strip=True)
    
    main = soup.find("main") if soup.find("main") else None
    if main:
        content_for_llm["main"] = main.get_text(separator="\n", strip=True)
    
    content_div = None
    for id_name in ["content", "post", "article"]:
        content_div = soup.find("div", id=id_name) if soup.find("div", id=id_name) else None
        if content_div:
            content_for_llm["content_div"] = content_div.get_text(separator="\n", strip=True)
            break
    
    paragraphs = soup.find_all("p") if soup.find_all("p") else []
    if paragraphs:
        para_texts = [p.get_text(separator="\n", strip=True) for p in paragraphs if p.get_text(strip=True)]
        content_for_llm["paragraphs"] = "\n".join(para_texts)
    
    headers = []
    for level in range(1, 7):
        headers.extend(soup.find_all(f"h{level}"))
        if headers:
            header_texts = [h.get_text(separator="\n", strip=True) for h in headers if h.get_text(strip=True)]
            content_for_llm["headers"] = "\n".join(header_texts)
            break

    driver.quit()

    return content_for_llm

def create_driver():
    options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options = options)
    return driver


def access_url(url: str, driver):
    """
    Tool to access a URL and perform a search query.
    Args:
        url (str): The URL to access.
        search_query (str): The search query to input.
    """
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    return "URL accessed successfully."



        

if __name__ == "__main__":
    url = "https://www.google.com"
    search_query = "OpenAI"
    result = interact_with_website_to_get_to_the_first_link(url, search_query)
    dump_json_to_file(result, "extracted_content.json")
    print("Done")
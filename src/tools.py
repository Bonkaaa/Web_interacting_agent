from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time, random

def interact_with_website_to_get_to_the_first_link(url, search_query, action="click", wait_time=10):
    """
    Interact with a website using Selenium WebDriver.
    Args:
        url (str): The URL of the website to interact with.
        search_query (str): The search query to input.
        action (str): The action to perform ("click" or "get_text").
        wait_time (int): Maximum wait time for elements to load.
    """
    # options = Options()
    # options.add_argument("--headless")  # Run in headless mode
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=options)

    # try:
    #     driver.get(url)
    #     WebDriverWait(driver, wait_time).until(
    #         EC.presence_of_element_located((By.ID, element_id))
    #     )
    #     element = driver.find_element(By.ID, element_id)

    #     if action == "click":
    #         element.click()
    #         return None
    #     elif action == "get_text":
    #         return element.text
    #     else:
    #         raise ValueError("Unsupported action. Use 'click' or 'get_text'.")
    # except TimeoutException:
    #     print(f"Element with ID '{element_id}' not found within {wait_time} seconds.")
    #     return None
    # finally:
    #     driver.quit()

    options = Options()
    options.add_argument("--headless")
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
    search_box.send_keys(Keys.Enter)

    time.sleep(5)

    current_url = driver.current_url

    if "captcha" in current_url.lower() or "sorry" in current_url.lower():
        print("Captcha detected! Please solve it manually...")
        input("Press Enter after solving the captcha to continue...")
    else:
        print("Search completed successfully!")

    try: 
        titles = driver.find_element(By.TAG_NAME, "h3")
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


    time.sleep(30)

    driver.quit()     
WEB_INTERACTING_AGENT_SYSTEM_PROMPT = """
You are a web-interacting agent. Your goal is to navigate to a website and find the first link on the page.
You will be provided with a URL and a search query. Use the provided tool to interact with the website.
"""

WEB_INTERACTING_AGENT_USER_PROMPT = """
Given the URL: {url} and the search query: {search_query}, use the tool to navigate to the website and find the first link on the page.
Return the text of the first link you find.
Make sure to follow the instructions carefully and use the tool as needed.
"""
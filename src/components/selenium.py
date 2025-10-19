from .llm import get_llm
from .template import selenium_prompt
from .tools import tools


def create_selenium_agent():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(tools=tools)


    selenium_agent = selenium_prompt | llm_with_tools

    return selenium_agent

    
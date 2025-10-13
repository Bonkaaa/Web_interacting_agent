from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from google.genai import types

from .utils import setup_logger
from .api import get_llm
from .tools import interact_with_website_to_get_to_the_first_link

from .prompts import WEB_INTERACTING_AGENT_SYSTEM_PROMPT, WEB_INTERACTING_AGENT_USER_PROMPT

from typing_extensions import TypedDict, Annotated

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    response: str
    url: str

def create_agent():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        [interact_with_website_to_get_to_the_first_link]
    )


    def tool_calling_llm():
        search_query = State["request"]
        url = State["url"]

        system_prompt = WEB_INTERACTING_AGENT_SYSTEM_PROMPT
        user_prompt = WEB_INTERACTING_AGENT_USER_PROMPT.format(
            url=url,
            search_query=search_query
        )

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            max_output_tokens=512,
            top_k=0.9
        )

        response = llm.models.generate_content(
            model="gemini-2.5-pro",
            config=config,
            messages=[
                HumanMessage(content=user_prompt)
            ]
        )

        return response.choices[0].message.content


    graph_builder = StateGraph[State]
    
    graph_builder.add_node("interact_with_website", func=tool_calling_llm, name="Interact with Website to Find First Link")
        

    
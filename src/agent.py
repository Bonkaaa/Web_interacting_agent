from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage

from .utils import setup_logger
from .llm import get_llm
from .tools import interact_with_website_to_get_to_the_first_link

from .prompts import WEB_INTERACTING_AGENT_SYSTEM_PROMPT, WEB_INTERACTING_AGENT_USER_PROMPT, SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_USER_PROMPT

from typing_extensions import TypedDict, Annotated


logger = setup_logger("agent")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    response: str
    response_summary: str
    url: str

def create_agent():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        [interact_with_website_to_get_to_the_first_link]
    )


    def tool_calling_llm_node(state: State) -> State:
        search_query = state["request"]
        url = state["url"]

        system_prompt = WEB_INTERACTING_AGENT_SYSTEM_PROMPT
        user_prompt = WEB_INTERACTING_AGENT_USER_PROMPT.format(
            url=url,
            search_query=search_query
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        state["messages"].extend(messages)

        try:
            response = llm_with_tools.invoke(messages)
            cleaned_response = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during LLM tools calling: {e}")
            cleaned_response = "Error: Unable to get response from LLM."

        logger.info(f"LLM Response: {cleaned_response}")
        state["response"] = cleaned_response
        state["messages"].append(AIMessage(content=cleaned_response))

        return state

    def summarize_node(state: State) -> State:
        tool_response = state["response"]

        system_prompt = SUMMARIZATION_SYSTEM_PROMPT
        user_prompt = SUMMARIZATION_USER_PROMPT.format(
            response_text=tool_response
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        state["messages"].extend(messages)

        try: 
            response = llm.invoke(messages)
            cleaned_response = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during LLM summarization: {e}")
            cleaned_response = "Error: Unable to get response from LLM."

        state["response_summary"] = cleaned_response
        logger.info(f"Summarization Response: {cleaned_response}")
        state["messages"].append(AIMessage(content=cleaned_response))

        return state


    def build_graph() -> StateGraph:
        graph = StateGraph(State)

        graph.add_node("tool_calling_llm", tool_calling_llm_node)
        graph.add_node("summarize", summarize_node)

        graph.add_edge(START, "tool_calling_llm")
        graph.add_edge("tool_calling_llm", "summarize")
        graph.add_edge("summarize", END)

        return graph.compile()
    

    graph = build_graph()

    return graph


if __name__ == "__main__":
    agent = create_agent()

    initial_state: State = {
        "messages": [],
        "request": "Hello world Python programming",
        "response": "",
        "response_summary": "",
        "url": "https://www.google.com"
    }

    final_state = agent.invoke(initial_state)

    print("\nFinal Response Summary:")
    print(final_state["response_summary"])
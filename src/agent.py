from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage

from .utils import setup_logger
from .llm import get_llm
from .tools import tools

from .prompts import WEB_INTERACTING_AGENT_SYSTEM_PROMPT, WEB_INTERACTING_AGENT_USER_PROMPT, SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_USER_PROMPT

from typing_extensions import TypedDict, Annotated


logger = setup_logger("agent")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    response: str
    response_summary: str
    url: str
    tool_call_count: int

def create_agent():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        tools=tools,
    )


    def interacting_web_node(state: State) -> State:
        system_prompt = WEB_INTERACTING_AGENT_SYSTEM_PROMPT
        user_prompt = WEB_INTERACTING_AGENT_USER_PROMPT.format(
            url=state["url"],
            request=state["request"]
        )
        
        # Only add system and user messages if messages list is empty
        if not state["messages"]:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            state["messages"].extend(messages)
        
        try:
            response = llm_with_tools.invoke(state["messages"])
            cleaned_response = response.content.strip()

            if not hasattr(response, 'tools_calls') or not response.tools_calls:
                state["response"] = cleaned_response

            state["messages"].append(AIMessage(content=cleaned_response))
            logger.info(f"Interacting Web Response: {cleaned_response}")

        except Exception as e:
            logger.error(f"Error during LLM interaction: {e}")
            state["response"] = "Error: Unable to get response from LLM."
            state["messages"].append(AIMessage(content=state["response"]))
        
        return state

    
    def should_continue(state: State):
        last_message = state["messages"][-1] if state["messages"] else None
        # tool_count = state.get("tool_call_count", 0)

        # if tool_count >= 5:
        #     return 'summarize'

        if isinstance(last_message, AIMessage):
            # Check if the last message has tool calls
            if hasattr(last_message, 'tools_calls') and last_message.tools_calls:
                return 'tools'
        return 'summarize'
        

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
            cleaned_response = response.content.strip()
        except Exception as e:
            logger.error(f"Error during LLM summarization: {e}")
            cleaned_response = "Error: Unable to get response from LLM."

        state["response_summary"] = cleaned_response
        logger.info(f"Summarization Response: {cleaned_response}")
        state["messages"].append(AIMessage(content=cleaned_response))

        return state


    def build_graph() -> StateGraph:
        graph = StateGraph(State)

        # Add nodes
        graph.add_node("interacting_web", interacting_web_node)
        graph.add_node("summarize", summarize_node)

        # Define workflow
        graph.add_edge(START, "interacting_web")

        graph.add_conditional_edges(
            "interacting_web",
            should_continue,
            {
                'tools': "tools",
                'summarize': "summarize"
            }
        )
        
        # Loop back to interacting_web after tools execution
        graph.add_edge('tools', "interacting_web")

        # Final edge to END after summarization
        graph.add_edge("summarize", END)

        return graph.compile()
    

    return build_graph()


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
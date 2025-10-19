from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from utils import setup_logger
from components.llm import get_llm
from components.tools import tools

from components.planner import create_planner
from components.selenium import create_selenium_agent
from components.summarize import create_summarizer_agent
from prompts import PLANNING_USER_PROMPT, SELENIUM_USER_PROMPT, SUMMARIZE_USER_PROMPT

from typing_extensions import TypedDict, Annotated
import json


logger = setup_logger("agent")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    summary: str
    url: str
    tool_call_count: int
    plan: dict
    llm_response: dict

planner = create_planner()
selenium_agent = create_selenium_agent()

tool_node = ToolNode(tools=tools)

def planning_node(state: State) -> State:

    user_prompt = PLANNING_USER_PROMPT.format(request=state["request"])

    request = [
        HumanMessage(content=user_prompt)
    ]

    try:
        plan = planner.invoke(
            {
                "request": request[0].content
            }
        )
        list_plan = plan.steps
        logger.info(f"Generated Plan: {list_plan}")

        state["plan"] = list_plan

        state["messages"].extend(request[0])
        state["messages"].append(AIMessage(content=json.dumps(dict(plan))))

    except Exception as e:
        logger.error(f"Error in planning_node: {e}")
        state["plan"] = {"steps": []}
        
    return state
    
def selenium_node(state: State) -> State:
    plan = state.get("plan", {})

    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan.get("steps", [])))

    tool_call_count = state.get("tool_call_count", 0)

    task = plan.get("steps", [])[tool_call_count] if tool_call_count < len(plan.get("steps", [])) else ""

    user_prompt = SELENIUM_USER_PROMPT.format(plan_str=plan_str, task=task)

    if not task:
        end_messages = [
            HumanMessage(content="No more steps to execute. No tool call needed.")
        ]
        response = selenium_agent.invoke(
            {
                "steps": end_messages[0].content,
            }
        )
        state["response"] = response

        return state
    try: 
        messages = [
            HumanMessage(content=user_prompt)
        ]

        selenium_response = selenium_agent.invoke(
            {
                "step": messages[0].content,
            }
        )
        logger.info(f"Selenium Agent Response for step '{task}': {selenium_response.content}")

        state["messages"].append(messages[0])
        state["messages"].append(AIMessage(content=selenium_response.content))

        state["llm_response"] = selenium_response

    except Exception as e:
        logger.error(f"Error in selenium_node: {e}")
        state["llm_response"] = f"Error executing step '{task}': {e}"
        
    return state
    
def route_workflow_node(state: State):
    tool_call_count = state.get("tool_call_count", 0)
    llm_response = state.get("llm_response", "")

    if "Error" in state.get("llm_response", ""):
        return "agent"
    elif tool_call_count + 1 < len(state.get("plan", {}).get("steps", [])) or "No tool call needed" in state["messages"][-1].content.strip().lower() or not llm_response["tool_calls"]:
        # if isinstance(llm_response.content, dict):
        return "summarize"
        
        ### Add replanner
        
    tool_call_count += 1
    state["tool_call_count"] = tool_call_count
    return "tools"

def summarize_node(state: State):


    summarization_agent = create_summarizer_agent()

    summary_dict = dict(state["llm_response"].content)

    try:
        user_prompt = SUMMARIZE_USER_PROMPT.format(
            html_content=summary_dict
        )

        messages = [
            HumanMessage(content=user_prompt)
        ]

        summary_response = summarization_agent.invoke(
            {
                "html_content": messages[0].content
            }
        )

        logger.info(f"Summarization Response: {summary_response.content}")
        
        state["messages"].append(messages[0])
        state["messages"].append(AIMessage(content=summary_response.content))

        state["summary"] = summary_response.content

    except Exception as e:
        logger.error(f"Error in summarize_node: {e}")
        state["summary"] = f"Error during summarization: {e}"
        
    return {"summary": state["summary"]}





# if __name__ == "__main__":
#     agent = create_agent()

#     initial_state: State = {
#         "messages": [],
#         "request": "Search for the term 'LangGraph' on the page and provide a summary of the content found.",
#         "response": "",
#         "response_summary": "",
#         "url": "http://localhost:8000/index.html"
#     }

#     final_state = agent.invoke(initial_state)

#     print("\nFinal Response Summary:")
#     print(final_state["response_summary"])
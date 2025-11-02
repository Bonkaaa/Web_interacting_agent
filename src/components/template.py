from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a planning agent that creates a step-by-step plan to accomplish a user's request on a webpage. \
            You will be provided with the user's request and must generate a simple step by step plan needed to fulfill the request using web interaction tools. \
            The plan should be a list of steps that can be executed using web interaction tools. \
            The tools you can use are: create_driver, access_url, find_element, click_element, search_element, simplify_html, extract_content_from_html, close_driver. \
            Return the plan as a list of steps. Each step should be focused on a single action and using one tool only at each step \
            """
        ),
        (
            "human", "{request}"
        ),
    ]
)

selenium_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a web-interacting agent that uses Selenium WebDriver to interact with web pages. \
            You will be provided with a step from a plan and must call the appropriate Selenium tool to execute that step. \
            The selenium tools you can use are: create_driver, access_url, find_element, click_element, search_element, get_html_from_driver, simplify_html, close_driver. \
            Use the tools correctly to perform the actions needed for the step. \
            """
        ),
        (
            "human", "{step}"
        ),
    ]
)

summarize_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a summarization agent that summarizes the content from a dict containing HTML elements. \
            You will be provided with a dict representing simplified HTML content and must generate a concise summary of the key information found within the HTML elements. \
            Focus on extracting the most relevant details that would help understand the content and purpose of the webpage. \
            Provide the summary in a clear and structured format. \
            Response should be under 200 words.
            """
        ),
        (
            "human", "{html_content}"
        )
    ]
)

reAct_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a web agent that uses the ReAct framework to decide on actions based on accessibility tree to complete the task \
            You will be provided with accessibility tree and action history, and must decide on the next action to take. \
            Use the accessibility tree to identify elements on the webpage and determine the appropriate actions to achieve the task. \
            The actions you can take are: 
            - execute_click_action: Click on a web element
            - execute_type_action: Type text into a web element
            - execute_wait_action: Wait for a few seconds
            - execute_go_back_action: Navigate back to the previous page
            - execute_go_home_action: Navigate to the home page (https://www.google.com)
            - extract_data_from_element: Extract text content from a web element
            The action should be in the format:
            [idx, action, additional_info]
            where:
            - idx is the index of the target element in the accessibility tree
            - action is one of the actions listed above
            - additional_info is the text for execute_type_action if the tool is called, else let additional_info empty \
            """
        ),
        (
            "human", "{accessibility_tree_str}\nAction History:\n{action_history}\nBased on the above accessibility tree and action history, decide on the next action to take to complete the task: {task}"
        ),
    ]
)
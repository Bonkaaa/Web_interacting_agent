from langchain_core.prompts import ChatPromptTemplate

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
            "human", "Accessibility Tree:\n{accessibility_tree_str}\nAction History:\n{action_history}\nBased on the above accessibility tree and action history, decide on the next action to take to complete the task: {task}"
        ),
    ]
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            """You are an agent that response the final answer for the user's task based on the given information \
            You will be provided with the extracted information from web elements, current accessibility tree, and user's task. \
            Synthesize the information to provide a concise and accurate answer to the user's task. \
            If the information is insufficient, respond with 'Insufficient information to provide an answer.' 
            The final answer should be under 50 words."""
        ),
        (
            'human', 'Extracted Information:\n{extracted_info}\nAccessibility Tree:\n{accessibility_tree_str}\nUser Task:\n{task}\nBased on the above information, provide the final answer.'
        ),
    ]
)
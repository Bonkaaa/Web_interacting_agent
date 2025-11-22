# PLANNING_USER_PROMPT = """
# Create a step-by-step plan to accomplish the user's request on a webpage.
# The plan should be a list of steps that can be executed using web interaction tools.
# Focus on creating clear and actionable steps that utilize the available tools effectively.

# ### User Request:
# {request}
# """

# SELENIUM_USER_PROMPT = """
# For the following plan: \n
# {plan_str}
# You are tasked with executing step: {task}
# Use one selenium tools to perform the actions needed for the step.
# """

# SUMMARIZE_USER_PROMPT = """
# Summarize the key information from the following simplified HTML content:
# {html_content}
# Provide a concise summary that captures the main points and relevant details.
# Focus on extracting the most important information that would help understand the content and purpose of the webpage.
# Response should be under 200 words.
# """

SUMMARIZE_USER_PROMPT = """


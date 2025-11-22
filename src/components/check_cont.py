from pydantic import BaseModel, Field

from .llm import get_llm
from .template import check_continue_prompt

from typing import List

class CheckContinueSchema(BaseModel):
    decision: str = Field(
        description="The decision on whether to continue web interaction or provide the final answer. Should be either 'FINAL ANSWER' or 'CONTINUE'."
    )

def create_check_continue_agent():
    llm = get_llm()

    check_continue = check_continue_prompt | llm.with_structured_output(CheckContinueSchema)

    return check_continue
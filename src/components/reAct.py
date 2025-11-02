from pydantic import BaseModel, Field

from .llm import get_llm
from .template import reAct_prompt

from typing import List, Union

class ReActSchema(BaseModel):
    thought: str = Field(
        description="The agent's thought process about what to do next."
    )
    action: List[Union[int, str, str]] = Field(
        description="The action to take, represented as a list where the first element is the element index from the accessibility tree, the second element is the action type (e.g., 'click', 'extract', 'search') and the third element is any additional information needed for the action."
    )
def reAct_agent():
    llm = get_llm()

    reAct = reAct_prompt | llm.with_structured_output(ReActSchema)

    return reAct
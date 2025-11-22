from pydantic import BaseModel, Field

from components.llm import get_llm
from components.template import answer_prompt

class AnswerSchema(BaseModel):
    answer: str = Field(
        description="The final answer synthesized from the extracted information and accessibility tree."
    )

def create_answer_agent():
    llm = get_llm()

    answer = answer_prompt | llm.with_structured_output(AnswerSchema)

    return answer
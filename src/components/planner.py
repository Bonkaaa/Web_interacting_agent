from pydantic import BaseModel, Field

from .template import planner_prompt
from .llm import get_llm

class PlanSchema(BaseModel):
    steps: list[str] = Field(
        description="A list of steps to accomplish the user's request on the webpage."
    )

def create_planner():
    llm = get_llm()

    planner = planner_prompt | llm.with_structured_output(PlanSchema)

    return planner


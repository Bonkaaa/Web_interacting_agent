from pydantic import BaseModel, Field

from components.llm import get_llm
from components.template import summarize_prompt

class SummarySchema(BaseModel):
    summary: str = Field(
        description="A concise summary of the key information found within the HTML elements."
    )

def create_summarizer_agent():
    llm = get_llm()

    summarizer = summarizer_prompt | llm.with_structured_output(SummarySchema)

    return summarizer
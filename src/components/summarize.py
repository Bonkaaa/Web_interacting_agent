from pydantic import BaseModel, Field
from .template import summarizer_prompt
from .llm import get_llm

class SummarySchema(BaseModel):
    summary: str = Field(
        description="A concise summary of the key information found within the HTML elements."
    )

def create_summarizer_agent():
    llm = get_llm()

    summarizer = summarizer_prompt | llm.with_structured_output(SummarySchema)

    return summarizer
from langchain.agents import create_agent

from models import model, SYSTEM_PROMPT
from Tools import search
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from typing import TypedDict, Annotated, Literal

from pydantic import BaseModel, Field

from industries import INDUSTRIES

class SubSectorState(TypedDict):
        sub_sector: str
        industry: str
        queries: list[str]
        findings: list[str]
        valid_findings: bool
        retries: int
        summary: str

#creates the queries to be sent to the LLM
def define_queries(state: SubSectorState):
        sector = state.sub_sector
        industry = state.industry
        current_retries = state.retries

        for trusted_site in INDUSTRIES[industry][sector]:
                message = [{'role': 'system', 'content': f'You are to generate a query to be sent to an LLM that will be used to search'}]
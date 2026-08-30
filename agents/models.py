import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
import uuid


load_dotenv()
Anthropic_key = os.getenv("ANTHROPIC_API_KEY=")

search = TavilySearch(max_results=5)

model = init_chat_model(
    model="anthropic:claude-sonnet-5"
)

config = {'configurable': {'thread_id': uuid.uuid4()}}

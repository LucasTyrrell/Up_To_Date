import os

from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model


Anthropic_key = os.getenv("ANTHROPIC_API_KEY=")

model = init_chat_model("anthropic:claude-haiku-4-5")


from langchain.agents import create_agent

from models import model
from Tools import tools

agent = create_agent(
        model=model,
        name = "Up-To_Date_Agent",
        tools = tools
)
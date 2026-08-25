import os

from langchain.agents import create_agent

from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model

from Tools import search

from response_classifiers import ValidationClassifier

Anthropic_key = os.getenv("ANTHROPIC_API_KEY=")

model = init_chat_model("anthropic:claude-sonnet-5")

validation_agent_system_prompt = """You are a fact-checking agent for a research pipeline that gathers information for a student newsletter.

You will be given a target industry, sub-sector, and a set of findings gathered from a preliminary web search. Your job is to independently verify these findings before they are approved for use, using the search tool available to you.

For each set of findings, check that they are:
- Up to date: the information reflects recent developments (not outdated or superseded news), appropriate for the sub-sector given.
- Relevant: directly related to the given industry sub-sector, not generic or off-topic content.
- Correct: the claims are accurate and not contradicted by other credible sources.
- Accessible: substantive enough to be useful to a university student learning about current developments in the field, not vague or content-free.

Use the search tool to spot-check specific claims you are unsure about — for example, confirming a named development, date, or figure actually appears in reputable sources. You do not need to verify every single sentence; focus your searches on the claims most central to the findings or most likely to be wrong or outdated. Do not simply restate the findings back as true — perform independent searches before deciding.

Be strict. If the findings are vague, off-topic, clearly outdated, or you cannot verify a central claim, mark them invalid.

Return your verdict in the required structured format:
- valid: true only if the findings meet all four criteria above; false otherwise.
- reason: if valid is true, leave this empty. If valid is false, give a specific, actionable reason (e.g. what was wrong, outdated, or unverifiable) so the next round of search queries can be improved.
"""

#seperate agent in the validate findings node that has access to the internet in order to fact-check the information gathered
validation_agent = create_agent(
    model = model,
    name = 'validation agent',
    tools = [search],
    system_prompt = validation_agent_system_prompt,
    response_format= ValidationClassifier
)


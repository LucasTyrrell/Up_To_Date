import asyncio

from agents.state import State
from tavily import AsyncTavilyClient
from agents.models import model
from datetime import datetime
from agents.response_classifiers import QueriesClassifier
from agents.newsletter.prompts import DEFINE_QUERIES_SYSTEM_PROMPT

class BaseScout:
    def __init__(self):
        self.client = AsyncTavilyClient()
        self.model = model
        self.tavily_threshold = 0.4

        self.content = []

    async def define_queries(self, state: State, prompt):
        # create queries to be used by the scouts to gather information
        try:
            company = state.get('company')
            role = state.get('role')
            date = datetime.now()

            user_message = prompt.format(company=company, role=role, date=date)
            system_message = DEFINE_QUERIES_SYSTEM_PROMPT

            #returns a list of queries
            structured_llm =  self.model.with_structured_output(QueriesClassifier)

            response = await structured_llm.ainvoke([
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message},
            ])

            return response.queries

        except Exception as e:
            return {"error": f"Error: {e}"}

    async def extract_content(self, state: State, findings: list[dict]):
        # gathers all the content from the findings
        try:
            content = []

            for item in findings:
                extracted = await self.client.extract(item['result']['url'])
                content.append({'query': item['query'], 'result': extracted})

            return content

        except Exception as e:
            return {"error": f"Error: {e}"}

    async def search(self, queries):
        try:
            response = await asyncio.gather(*[self.client.search(query) for query in queries])
            findings = []

            #filters through all results to only include most relevant results
            for query, item in zip(queries, response):
                for result in item['results']:
                    if result["score"] > self.tavily_threshold:
                        findings.append({'query': query, 'result': result})

            #sorts them in order of relevance, and using only the 10 most relevant
            sorted_findings = sorted(findings, key=lambda x: x['result']['score'], reverse=True)

            return sorted_findings[:10]

        except Exception as e:
            return {"error": f"Error: {e}"}
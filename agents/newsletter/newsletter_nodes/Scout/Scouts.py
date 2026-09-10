from agents.newsletter.newsletter_nodes.Scout.BaseScout import BaseScout
from agents.state import State
from agents.newsletter.prompts import *

class CompanyScout(BaseScout):
        async def run(self, state: State) -> dict:
            queries = await self.define_queries(state, COMPANY_SCOUT_QUERY_PROMPT)

            findings = await self.search(queries)

            return {"company_info_findings": findings}


class RoleScout(BaseScout):
        async def run(self, state: State) -> dict:
            queries = await self.define_queries(state, ROLE_SCOUT_QUERY_PROMPT)

            findings = await self.search(queries)

            return {"role_findings": findings}


class NewsScout(BaseScout):
    async def run(self, state: State) -> dict:
        queries = await self.define_queries(state, NEWS_SCOUT_QUERY_PROMPT)

        findings = await self.search(queries)

        return {"company_news_findings": findings}


class InterviewScout(BaseScout):
    async def run(self, state: State) -> dict:
        queries = await self.define_queries(state, INTERVIEW_SCOUT_QUERY_PROMPT)

        findings = await self.search(queries)

        return {"interview_findings": findings}
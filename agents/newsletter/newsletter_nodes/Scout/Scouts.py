from agents.newsletter.newsletter_nodes.Scout.BaseScout import BaseScout
from agents.state import State
from agents.newsletter.prompts import *

class CompanyScout(BaseScout):
        async def run(self, state: State) -> dict:
            queries = await self.define_queries(state, COMPANY_SCOUT_QUERY_PROMPT)

            findings = await self.search(queries)

            content = await self.extract_content(state, findings)

            return {"company_info_findings": content}


class RoleScout(BaseScout):
        async def run(self, state: State) -> dict:
            queries = await self.define_queries(state, ROLE_SCOUT_QUERY_PROMPT)

            findings = await self.search(queries)

            content = await self.extract_content(state, findings)

            return {"role_findings": content}


class NewsScout(BaseScout):
    async def run(self, state: State) -> dict:
        queries = await self.define_queries(state, NEWS_SCOUT_QUERY_PROMPT)

        findings = await self.search(queries)

        content = await self.extract_content(state, findings)

        return {"company_news_findings": content}


class InterviewScout(BaseScout):
    async def run(self, state: State) -> dict:
        queries = await self.define_queries(state, INTERVIEW_SCOUT_QUERY_PROMPT)

        findings = await self.search(queries)

        content = await self.extract_content(state, findings)

        return {"interview_findings": content}
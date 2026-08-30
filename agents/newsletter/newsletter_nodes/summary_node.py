from agents.state import State
from agents.models import model
from agents.newsletter.prompts import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT


class Summary:
    def run(self, state: State) -> dict:
        try:
            company = state.get('company')
            role = state.get("role")
            industry = state.get('industry')

            company_info_findings = state.get('company_info_findings')
            role_findings = state.get('role_findings')
            company_news_findings = state.get('company_news_findings')
            interview_findings = state.get('interview_findings')


            response = model.invoke([
                {'role': 'system', 'content': SUMMARY_SYSTEM_PROMPT},
                {'role': 'user', 'content': SUMMARY_USER_PROMPT.format(
                    company=company, role=role, industry=industry, company_info_findings=company_info_findings,
                    role_findings=role_findings, company_news_findings=company_news_findings, interview_findings=interview_findings)},
            ])
            return {'summary': response.content}
        except Exception as e:
            return {"summary": f"Error: {e}"}


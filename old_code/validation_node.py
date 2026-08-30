from agents.models import validation_agent
from agents.state import State
from datetime import datetime
from agents.newsletter.prompts import VALIDATION_AGENT_SYSTEM_PROMPT, VALIDATION_USER_PROMPT
from typing import Literal


class Validation:
    def run(self, state: State) -> dict:
        try:
            findings = state.get('findings')
            industry = state.get('industry')
            sector = state.get('sub_sector')
            retries = state.get('retries') or 0
            message = VALIDATION_USER_PROMPT.format(
                findings=findings, current_date=datetime.now(), industry=industry, sector=sector
            )

            response = validation_agent.invoke({'messages': [
                {'role': 'system', 'content': VALIDATION_AGENT_SYSTEM_PROMPT},
                {'role': 'user', "content": message},
            ]})
            validation = response['structured_response']
            if not validation.valid:
                retries += 1
                return {'valid_findings': validation.valid, 'reason': validation.reason, 'retries': retries}
            else:
                return {'valid_findings': validation.valid}
        except Exception as e:
                return {"summary": f"Error: {e}", "retries": (state.get('retries') or 0) + 1}

    def route(self, state: State) -> Literal['define_queries', 'summarise']:
        if state.get('valid_findings') or (state.get('retries') or 0) >= 3:
            return 'summarise'
        else:
            return 'define_queries'
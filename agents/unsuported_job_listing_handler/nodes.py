from agents.models import model
from agents.response_classifiers import IsJobListingClassifier, UnsupportedClassifier
from agents.unsuported_job_listing_handler.prompts import (
    IS_JOB_LISTING_SYSTEM_PROMPT, IS_JOB_LISTING_USER_PROMPT,
    EXTRACT_LISTING_SYSTEM_PROMPT, EXTRACT_LISTING_USER_PROMPT,
)
from agents.unsuported_job_listing_handler.state import UnsupportedListingState


#gate node - confirms the scraped page is actually a job listing before extraction is attempted
class ListingGate:
    def run(self, state: UnsupportedListingState) -> dict:
        try:
            structured_llm = model.with_structured_output(IsJobListingClassifier)

            response = structured_llm.invoke([
                {'role': 'system', 'content': IS_JOB_LISTING_SYSTEM_PROMPT},
                {'role': 'user', 'content': IS_JOB_LISTING_USER_PROMPT.format(
                    url=state['url'], page_text=state['page_text'])},
            ])

            if not response.is_job_listing:
                return {'is_job_listing': False, 'error': response.reason}

            return {'is_job_listing': True}

        except Exception as e:
            return {'error': f"Could not verify listing: {e}"}


#pulls the listing fields out of a page already confirmed to be a job listing
class ListingExtractor:
    def run(self, state: UnsupportedListingState) -> dict:
        try:
            structured_llm = model.with_structured_output(UnsupportedClassifier)

            response = structured_llm.invoke([
                {'role': 'system', 'content': EXTRACT_LISTING_SYSTEM_PROMPT},
                {'role': 'user', 'content': EXTRACT_LISTING_USER_PROMPT.format(
                    url=state['url'], page_text=state['page_text'])},
            ])

            return {
                'role_title': response.role_title,
                'company_name': response.company_name,
                'salary': response.salary,
                'job_location': response.job_location,
                'role_type': response.role_type,
            }

        except Exception as e:
            return {'error': f"Could not extract listing: {e}"}
from agents.response_classifiers import RelevanceClassifier
from agents.models import model
from agents.job_relevance.prompts import RELEVANCE_SCORE_SYSTEM_PROMPT, RELEVANCE_SCORE_USER_PROMPT
from db.jobs_service import get_jobs_to_score, get_job_by_id, store_relevance_score, get_cv_content
import asyncio

#need to run parallel to other LLM calls if multiple listings require a relevance score
async def generate_relevance_score(listing, cv_text):
    try:

        structured_llm = model.with_structured_output(RelevanceClassifier).with_retry(stop_after_attempt=2)

        user_message = RELEVANCE_SCORE_USER_PROMPT.format(
            job_title=listing.role_title,
            company_name=listing.company_name,
            job_description=listing.description,
            cv_text=cv_text,
        )

        response = await structured_llm.ainvoke([
            {'role': 'system', 'content': RELEVANCE_SCORE_SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ])

        return {'score': response.score, 'positives': response.positives, 'negatives': response.negatives}

    except Exception as e:
        return {"error": f"Relevance scoring failed: {e}"}


#only scores jobs that have not previously been scored, for batch scoring
async def get_relevance_scores():
    jobs = get_jobs_to_score()
    CV = get_cv_content()

    if CV is None:
        return {"error": f"No CV uploaded"}

    results = await asyncio.gather(*(generate_relevance_score(job, CV) for job in jobs))

    for job, result in zip(jobs, results):
        if "error" in result:
            print(f"skipping {job.id}: {result['error']}")
            continue
        store_relevance_score(job.id, result['score'], result['positives'], result['negatives'])


#scores a single listing, regardless of whether it has already been scored
async def generate_relevance_score_for_listing(listing_id):
    job = get_job_by_id(listing_id)
    if job is None:
        return {"error": "Listing not found"}

    CV = get_cv_content()
    if CV is None:
        return {"error": "No CV uploaded"}

    result = await generate_relevance_score(job, CV)
    if "error" in result:
        return result

    store_relevance_score(job.id, result['score'], result['positives'], result['negatives'])
    return result

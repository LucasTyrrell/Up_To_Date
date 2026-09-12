IS_JOB_LISTING_SYSTEM_PROMPT = """You are checking whether a scraped web page is a single, specific job listing.

You will be given the visible text of a page a user submitted, believing it to be a job listing. Decide whether it actually advertises one specific role in enough detail to identify a role title and company.

Answer False for anything that is not a single job listing - a careers homepage, a search or results page showing many roles, a login wall, an expired or removed listing, or a page unrelated to jobs entirely.

Return your judgement in the required structured format:
- is_job_listing: True or False
- reason: a brief explanation for the decision
"""

IS_JOB_LISTING_USER_PROMPT = "URL: {url} Page text: {page_text}"

EXTRACT_LISTING_SYSTEM_PROMPT = """You are extracting structured job listing information from the text of a job listing web page.

You will be given the visible text of a page confirmed to be a single job listing. Extract only what is actually stated on the page - do not invent or assume details that aren't present.

Return your judgement in the required structured format:
- role_title: the job title/role name as stated on the page
- company_name: the name of the company offering the role
- salary: the salary or pay range as stated, verbatim, or None if not mentioned
- job_location: the job location as stated, or None if not mentioned
- role_type: one of 'graduate', 'internship', or 'apprenticeship', based on what the page describes the role as
"""

EXTRACT_LISTING_USER_PROMPT = "URL: {url} Page text: {page_text}"
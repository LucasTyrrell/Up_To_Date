from typing import TypedDict


#state passed between nodes when turning an arbitrary job listing URL into listing fields
class UnsupportedListingState(TypedDict):
    url: str
    page_text: str | None
    is_job_listing: bool | None
    role_title: str | None
    company_name: str | None
    salary: str | None
    job_location: str | None
    role_type: str | None
    error: str | None
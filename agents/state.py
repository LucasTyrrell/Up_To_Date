from typing import TypedDict




#defines the information that is to be passed to each LLM call
class State(TypedDict):
        company: str | None
        role: str | None
        industry: str | None
        company_info_findings: list[dict] | None
        company_news_findings: list[dict] | None
        role_findings: list[dict] | None
        interview_findings: list[dict] | None
        valid_findings: bool | None
        reason: str | None
        retries: int | None
        summary: str | None
        HTML: str | None
        PDF: bytes | None
        error: str | None
from typing import Literal

from doctest import debug_src

from pandas._libs.tslibs import fields
from pydantic import BaseModel, Field


#defines a structure for the LLM to follow when making the response
class QueriesClassifier(BaseModel):
        queries: list[str] = Field(description='5-10 concise queries to gain information relevant to the '
                                                'given sub sector using the trusted sites, the information'
                                                'gathered from these queries is to be relevant to university'
                                                'students wanting to keep up to date with current developments'
                                                'in the field')


class HTMLClassifier(BaseModel):
    HTML: str = Field(..., description='The HTML content of the website, this to be raw HTML nothing else')

class RelevanceClassifier(BaseModel):
    score: int = Field(..., ge=0, le=100, description='How well the candidates CV matches this job, from 0 to 100, '
                                                       'based on overlap between the CVs skills/experience and the '
                                                       'jobs stated requirements. 0 means no relevant overlap at all, '
                                                       '100 means the CV is an exact match for every requirement, '
                                                       'with scores in between reflecting partial overlap, missing '
                                                       'requirements, or seniority mismatch')

    positives: list[str] = Field(..., description='Specific, concrete ways the CV supports this application — '
                                                   'skills, experience, projects, or qualifications from the CV '
                                                   'that directly match something the job explicitly asks for. '
                                                   'Empty list if there is no genuine overlap')

    negatives: list[str] = Field(..., description='Specific, concrete gaps between the CV and this job — '
                                                   'requirements stated in the job that the CV does not show '
                                                   'evidence of, or mismatches (e.g. seniority level, required '
                                                   'skills the CV lacks). Empty list if there are no notable gaps')

#gates the unsupported-listing pipeline before extraction is attempted
class IsJobListingClassifier(BaseModel):
    is_job_listing: bool = Field(..., description='True if this page is a specific job listing - i.e. it '
                                                   'advertises one particular role with enough detail to identify '
                                                   'a role title and company. False if it is not a job listing - '
                                                   'e.g. a careers homepage, a search/results page listing many '
                                                   'roles, a login wall, a 404 or expired listing, or unrelated '
                                                   'content')

    reason: str = Field(..., description='Brief explanation for the decision')


#used to pull job listing fields out of a page from a site with no dedicated scraper
class UnsupportedClassifier(BaseModel):
    role_title: str = Field(..., description='The job title/role name as stated on the page')

    company_name: str = Field(..., description='The name of the company offering the role')

    salary: str | None = Field(None, description='The salary or pay range as stated on the page, verbatim. '
                                                  'None if no salary is mentioned')

    job_location: str | None = Field(None, description='The job location as stated on the page. '
                                                         'None if no location is mentioned')

    role_type: Literal['graduate', 'internship', 'apprenticeship'] = Field(
        ..., description='The type of role this listing is for, based on the page content')

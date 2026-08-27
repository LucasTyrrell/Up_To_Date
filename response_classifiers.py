from pydantic import BaseModel, Field


#defines a structure for the LLM to follow when making the response
class QueriesClassifier(BaseModel):
        queries: list[str] = Field(description='5-10 concise queries to gain information relevant to the '
                                                'given sub sector using the trusted sites, the information'
                                                'gathered from these queries is to be relevant to university'
                                                'students wanting to keep up to date with current developments'
                                                'in the field')

class ValidationClassifier(BaseModel):
        valid: bool = Field(..., description='True if the information gathered is:'
                                             '- up to date'
                                             '- relevant to university students'
                                             '- correct'
                                             'false otherwise')
        reason: str = Field(..., description='Reason for validation, if valid is true return nothing,'
                                             'if it is false return a detailed reason for the decision'
                                             'to aid with retreiving better information the next time ')

class HTMLClassifier(BaseModel):
    HTML: str = Field(..., description='The HTML content of the website, this to be raw HTML nothing else')
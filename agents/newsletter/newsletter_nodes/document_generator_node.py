from agents.newsletter.state import State
from agents.models import model
from agents.newsletter.prompts import HTML_GENERATOR_USER_PROMPT, HTML_GENERATOR_SYSTEM_PROMPT
from agents.response_classifiers import HTMLClassifier
from bs4 import BeautifulSoup
from io import BytesIO
from xhtml2pdf import pisa

class DocumentGenerator:
    def __init__(self):
        self.model = model
        self.structured_llm = model.with_structured_output(HTMLClassifier)


    def HTML_generator(self, state: State):
        try:
            role = state.get('role')
            company = state.get('company')
            industry = state.get('industry')
            summary = state.get('summary')

            response = self.structured_llm.invoke([{'role': 'system', 'content': HTML_GENERATOR_SYSTEM_PROMPT},
                                                   {'role': 'user', 'content': HTML_GENERATOR_USER_PROMPT.format(
                                                       role=role,company=company, industry=industry, summary=summary)}])

            HTML = BeautifulSoup(response.HTML, 'html.parser').prettify()

            return {'HTML': HTML}
        except Exception as e:
            return {"error": f"HTML generation failed: {e}"}

    def PDF_generator(self, state: State):
        html = state.get('HTML')
        if not html:
            return {"error": state.get('error') or "PDF generation skipped: no HTML was generated"}

        try:
            pdf_buffer = BytesIO()
            pisa.CreatePDF(html, pdf_buffer)

            pdf_buffer.seek(0)
            return {'PDF': pdf_buffer.getvalue()}
        except Exception as e:
            return {"error": f"PDF generation failed: {e}"}
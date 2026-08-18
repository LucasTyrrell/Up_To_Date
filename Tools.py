from langchain_community.tools import DuckDuckGoSearchResults
import streamlit as st
from langchain.tools import tool
from xhtml2pdf import pisa
from shared_state import pdf_buffer
search = DuckDuckGoSearchResults()

@tool
def GenerateNewsletter(query: str):
    """ ALWAYS CALL THIS ONCE A NEWSLETTER HAS BEEN GENERATED
        Call this tool to generate a newsletter in mark down format, with up-to-date information pertaining to the provided sub sectors
        the information should be no older than two weeks and should be substantial enough to fill one A4 page per sub sector
        if there is enough information present

        in order to retrieve the information use the search tool
        This will be displayed in Markdown format to the user using streamlit"""
    try:
        st.markdown(body=query, unsafe_allow_html=True)
    except Exception as e:
        return f"Error: {e}"

@tool
def create_pdf(query: str):
    """Once the HTML for the newsletter is created, use this tool in order to convert it into a PDF
        this is to be used only after the newsletter is completed. Only input raw HTML"""
    try:
        pisa.CreatePDF(query, pdf_buffer)
    except Exception as e:
        return f"Error: {e}"



tools = [search, create_pdf]
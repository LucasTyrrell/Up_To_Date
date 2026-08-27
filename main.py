import streamlit as st
from industries import INDUSTRIES

from Newsletter_agent import agent

import datetime
from shared_state import pdf_buffer

st.write("Up To Date Newsletter")

def get_selected_sub_sectors(industry):
    return [
        sub_sector
        for sub_sector in INDUSTRIES[industry]
        if st.session_state.get(sub_sector)
    ]


def GenerateNewsletter():
    selected_sub_sectors = get_selected_sub_sectors(st.session_state.selected_industry)
    if len(selected_sub_sectors) == 0:
        st.error("Please select at least one sub sector")
    else:
        response = agent.invoke({"messages": [{"role": "user", "content":
            f"Gather up to date date: {datetime.datetime.now()}information for the following sub sectors: {selected_sub_sectors}"}]})
        Newsletter = response["messages"][-1].content
        if Newsletter is not None:

            pdf_buffer.seek(0)
            st.pdf(pdf_buffer)

def industry_selected(industry_selected):
    if industry_selected in INDUSTRIES:
        st.subheader(f"Industry: {industry_selected}")
        for sub_sector in INDUSTRIES[industry_selected]:
            st.checkbox(sub_sector, key=sub_sector)
        st.button(label="Generate Newsletter", on_click=GenerateNewsletter)


industry_list = st.menu_button(label="Select Industry", options=INDUSTRIES)
if industry_list:
    st.session_state.selected_industry = industry_list

if "selected_industry" in st.session_state:
    industry_selected(st.session_state.selected_industry)

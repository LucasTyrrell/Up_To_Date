import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.jobs_service import get_all_job_listings, add_job_application
from scraper.gradcracker_scraper import run_scrape_gradcracker

st.set_page_config(page_title="Up To Date - Job Listings", layout="wide")

ROLE_TYPE_LABELS = {
    "graduate": "Graduate",
    "internship": "Internship",
    "apprenticeship": "Apprenticeship",
}

# only discipline gradcracker scraping currently supports — add more as scrapers are built
DISCIPLINE_LABELS = {
    "computing-technology": "Computing & Technology",
}

#cache listings as to not query database each time page is refreshed
@st.cache_data(ttl=300)
def load_listings():
    return get_all_job_listings()


def apply_to_job(listing_id):
    #add application to database
    add_job_application(listing_id)
    #clear cache as to not display a job that has been applied for
    load_listings.clear()


st.title("Job Listings")

listings = load_listings()

st.session_state.setdefault("applied", set())

with st.sidebar:
    st.header("Scrape new listings")

    scrape_discipline = st.selectbox(
        "Discipline",
        options=list(DISCIPLINE_LABELS),
        format_func=lambda d: DISCIPLINE_LABELS.get(d, d),
    )
    scrape_job_type = st.selectbox(
        "Job type",
        options=["graduate", "internship", "apprenticeship"],
        format_func=lambda rt: ROLE_TYPE_LABELS.get(rt, rt),
    )

    if st.button("Refresh listings", use_container_width=True):
        with st.spinner("Scraping new listings — this can take a few minutes..."):
            try:
                run_scrape_gradcracker(discipline=scrape_discipline, job_type=scrape_job_type, headless=True)
            except Exception as e:
                st.error(f"Scraping failed: {e}")
        load_listings.clear()
        st.rerun()

    st.divider()
    st.header("Filters")

    search = st.text_input("Search company or role")

    role_types = sorted({listing["role_type"] for listing in listings if listing["role_type"]})
    selected_role_types = st.multiselect(
        "Role type",
        options=role_types,
        format_func=lambda rt: ROLE_TYPE_LABELS.get(rt, rt),
    )

    locations = sorted({listing["job_location"] for listing in listings if listing["job_location"]})
    selected_locations = st.multiselect("Location", options=locations)

    sources = sorted({listing["job_source"] for listing in listings if listing["job_source"]})
    selected_sources = st.multiselect("Source", options=sources)

    hide_applied = st.checkbox("Hide applied", value=False)

if not listings:
    st.info("No job listings found yet. Use 'Refresh listings' in the sidebar to scrape some.")
    st.stop()


def matches_filters(listing):
    if search:
        haystack = f"{listing['company_name']} {listing['role_title']}".lower()
        if search.lower() not in haystack:
            return False

    if selected_role_types and listing["role_type"] not in selected_role_types:
        return False

    if selected_locations and listing["job_location"] not in selected_locations:
        return False

    if selected_sources and listing["job_source"] not in selected_sources:
        return False

    if hide_applied and listing["id"] in st.session_state["applied"]:
        return False

    return True


filtered = [listing for listing in listings if matches_filters(listing)]

st.caption(f"Showing {len(filtered)} of {len(listings)} listings")

for listing in filtered:
    with st.container(border=True):
        info_col, action_col = st.columns([5, 1])

        with info_col:
            title = listing["role_title"] or "Untitled role"
            company = listing["company_name"] or "Unknown company"
            st.subheader(f"{title} — {company}")

            details = []
            if listing["job_location"]:
                details.append(f" {listing['job_location']}")
            if listing["salary"]:
                details.append(f" {listing['salary']}")
            if listing["role_type"]:
                details.append(ROLE_TYPE_LABELS.get(listing["role_type"], listing["role_type"]))
            if listing["job_source"]:
                details.append(f"via {listing['job_source']}")

            if details:
                st.caption(" · ".join(details))

            if listing["url"]:
                st.markdown(f"[View original listing]({listing['url']})")

        with action_col:
            st.button(
                "Apply",
                key=f"apply_{listing['id']}",
                on_click=apply_to_job,
                args=(listing["id"],),
                use_container_width=True,
            )


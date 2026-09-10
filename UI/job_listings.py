import sys
import asyncio
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.jobs_service import (
    get_all_job_listings, add_job_application, add_job_application_from_scratch,
    get_cv_content, get_cv_pdf, store_cv,
)
from scraper.gradcracker_scraper import run_scrape_gradcracker
from agents.job_relevance.relevance_scorer import get_relevance_scores, generate_relevance_score_for_listing
from agents.unsuported_job_listing_handler.listing_scraper import get_job_application_from_url

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


def score_listing(listing_id):
    if not get_cv_content():
        st.session_state["score_error"] = {"listing_id": listing_id, "message": "No CV on file — upload one above before scoring."}
        return

    result = asyncio.run(generate_relevance_score_for_listing(listing_id))
    if isinstance(result, dict) and result.get("error"):
        st.session_state["score_error"] = {"listing_id": listing_id, "message": result["error"]}
    else:
        st.session_state.pop("score_error", None)
    load_listings.clear()


def add_from_link(url):
    if not url:
        st.session_state["link_error"] = "Enter a URL first."
        return

    result = get_job_application_from_url(url)
    if result.get("error"):
        st.session_state["link_error"] = result["error"]
        return

    add_job_application_from_scratch(
        url=result["url"],
        company_name=result["company_name"],
        role_title=result["role_title"],
        salary=result["salary"],
        job_location=result["job_location"],
        role_type=result["role_type"],
    )
    st.session_state.pop("link_error", None)
    st.session_state["link_added"] = f"{result['role_title']} at {result['company_name']}"
    load_listings.clear()


st.title("Job Listings")

with st.container(border=True):
    st.subheader("CV")

    cv_text = get_cv_content()

    if not cv_text:
        st.write("No CV on file yet — upload one to enable relevance scoring.")
        new_cv = st.file_uploader("Upload your CV (PDF)", type="pdf", key="cv_uploader_new")
        if new_cv is not None:
            store_cv(new_cv)
            st.success("CV uploaded.")
            st.rerun()
    else:
        view_col, change_col = st.columns(2)
        with view_col:
            if st.button("View CV", use_container_width=True):
                st.session_state["show_cv"] = not st.session_state.get("show_cv", False)
        with change_col:
            if st.button("Change stored CV", use_container_width=True):
                st.session_state["show_cv_uploader"] = not st.session_state.get("show_cv_uploader", False)

        if st.session_state.get("show_cv"):
            st.pdf(get_cv_pdf())

        if st.session_state.get("show_cv_uploader"):
            replacement_cv = st.file_uploader("Upload replacement CV (PDF)", type="pdf", key="cv_uploader_replace")
            if replacement_cv is not None:
                store_cv(replacement_cv)
                st.session_state["show_cv_uploader"] = False
                st.success("CV updated.")
                st.rerun()

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
                #headless=True hit gradcracker's cloudflare challenge on 2026-09-09 (worked headless before that,
                #so this looks intermittent rather than a fixed headless-vs-headed rule) - headed mode as a
                #safer default until we understand the trigger better
                run_scrape_gradcracker(discipline=scrape_discipline, job_type=scrape_job_type, headless=False)
            except Exception as e:
                st.error(f"Scraping failed: {e}")
        load_listings.clear()
        st.rerun()

    st.divider()
    st.header("Relevance scoring")

    if st.button("Generate relevance scores", use_container_width=True):
        if not get_cv_content():
            st.error("No CV on file — upload one above before scoring.")
        else:
            with st.spinner("Scoring listings against your CV..."):
                result = asyncio.run(get_relevance_scores())
            if isinstance(result, dict) and result.get("error"):
                st.error(result["error"])
            else:
                load_listings.clear()
                st.rerun()

    st.divider()
    st.header("Track a listing from a link")

    link_url = st.text_input("Job listing URL", key="manual_listing_url")
    if st.button("Add from link", use_container_width=True):
        with st.spinner("Reading the listing..."):
            add_from_link(link_url)

    if st.session_state.get("link_error"):
        st.error('Unfortunately, the we were not able to gather the data from this link')

    if st.session_state.get("link_added"):
        st.success(f"Added {st.session_state.pop('link_added')} to your applications.")

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
    scored_only = st.checkbox("Only show scored listings", value=False)

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

    if scored_only and listing["job_relevance_score"] is None:
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

            if listing["job_relevance_score"] is not None:
                st.progress(listing["job_relevance_score"] / 100, text=f"Relevance: {listing['job_relevance_score']}/100")

                if listing["positives"]:
                    with st.expander("Why it's a good fit"):
                        for point in listing["positives"]:
                            st.markdown(f"- {point}")

                if listing["negatives"]:
                    with st.expander("Gaps to be aware of"):
                        for point in listing["negatives"]:
                            st.markdown(f"- {point}")

        with action_col:
            st.button(
                "Apply",
                key=f"apply_{listing['id']}",
                on_click=apply_to_job,
                args=(listing["id"],),
                use_container_width=True,
            )
            st.button(
                "Generate score",
                key=f"score_{listing['id']}",
                on_click=score_listing,
                args=(listing["id"],),
                use_container_width=True,
            )

        score_error = st.session_state.get("score_error")
        if score_error and score_error["listing_id"] == listing["id"]:
            st.error(score_error["message"])


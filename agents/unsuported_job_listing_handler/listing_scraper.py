from patchright.sync_api import sync_playwright

from agents.unsuported_job_listing_handler.graph import UnsupportedJobListingHandler

#in order to support tracking of jobs for lisings outside of supported sites an LLM is used in order to gather -
#the information needed to create a JobLising and JobApplication object


#grabs the page's visible text - the layout of an arbitrary site is unknown ahead of time, so there's no
#selector to scope to, and raw HTML would bury the listing under script/style/nav noise
def scrape_page_text(playwright, url):
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir='C:\\playwright',
        channel='chrome',
        headless=True,
        no_viewport=True,
    )

    try:
        page = browser.new_page()
        page.goto(url, timeout=15000)
        return page.inner_text('body')
    finally:
        browser.close()


def get_job_application_from_url(url):
    with sync_playwright() as playwright:
        try:
            page_text = scrape_page_text(playwright, url)
        except Exception as e:
            return {"error": f"Could not load page: {e}"}

    handler = UnsupportedJobListingHandler()
    compiled_graph = handler.run()

    result = compiled_graph.invoke({
        "url": url,
        "page_text": page_text,
        "is_job_listing": None,
        "role_title": None,
        "company_name": None,
        "salary": None,
        "job_location": None,
        "role_type": None,
        "error": None,
    })

    if result.get("error"):
        return {"error": result["error"]}

    return {
        "url": url,
        "role_title": result["role_title"],
        "company_name": result["company_name"],
        "salary": result["salary"],
        "job_location": result["job_location"],
        "role_type": result["role_type"],
    }
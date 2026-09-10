from patchright.sync_api import sync_playwright
import time
from db.jobs_service import get_urls, add_job_listing

from scraper.clean_data import normalize_text, parse_salary, map_role_type


def scrape_gradcracker(playwright, discipline, job_type, headless=True):
    #initiate the browser
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir='C:\\playwright',
        channel='chrome',
        headless=headless,
        no_viewport=True,
    )

    #ensures the browser always gets closed, even if a page breaks the scrape
    try:
        #Listings already in database
        stored_urls = get_urls()

        #initiate page
        page = browser.new_page()

        #temp variables
        page_count = 1
        jobs = []

        EXCLUDED_KEYWORDS = ('webinar', 'insight', 'open-day', 'information-session',
                             'sneak-peak', 'inclusion', 'school-experience', 'virtual-recruitment')

        role_type = map_role_type(job_type)

        if job_type == 'placement' or job_type == 'internship':
            job_type = 'work-placements-internships'

        while page_count < 4:

            #setting delay as to avoid sending too many requests
            time.sleep(2)

            #a page number past the last available one can 404 or hang instead of
            #just rendering empty skip straight to the empty listings check below
            try:
                page.goto(f'https://www.gradcracker.com/search/{discipline}/{job_type}?page={page_count}', timeout=15000)
            except Exception as e:
                print(f'page {page_count} unavailable ({e}), stopping pagination')
                break

            listings = page.locator('article[wire\\:key] h2 a')

            try:
                listings.first.wait_for(state='visible', timeout=10000)
            except Exception:
                print(f'no listings found at {page.url} (page title: {page.title()!r})')
                break


            #getting the url from each article
            for listing in listings.element_handles():
                #prevents the scraper from adding company hub urls to jobs

                href = listing.get_attribute('href')
                #if href is None or href.count('/') < 5:
                    #continue

                title_el = listing.inner_text()

                if title_el is None or href is None:
                    continue


                if href is None:
                    continue

                item = {}

                item['title'] = title_el.strip()
                item['URL'] = href if href.startswith('http') else "https://www.gradcracker.com" + href

                #prevents searching and storing of duplicate listings
                #prevents wasting time running a deep search on a webinar or insight day
                if item['URL'] not in stored_urls:
                    if not any(keyword in item['URL'] for keyword in EXCLUDED_KEYWORDS):
                        jobs.append(item)

            page_count += 1

        #deep search into each job listing
        for job in jobs:

            #listings can 404, redirect, or time out once their deadline has passed -
            #skip a broken page instead of letting it kill the whole scrape run
            try:
                page.goto(job['URL'], timeout=15000)
            except Exception as e:
                print(f"skipping {job['URL']!r}: page unavailable ({e})")
                continue

            time.sleep(2)

            #srape doent get stuck on out of date lisings
            if page.locator('text=This position is no longer available').count() > 0:
                continue

            try:
                item = {}
                item['title'] = normalize_text(job['title'])
                item['URL'] = job['URL']
                item['description'] = None
                item['location'] = None
                item['salary'] = None
                item['company_name'] = None
                item['role_type'] = role_type
                item['source'] = 'gradcracker'

                #grabs all information from the info box on the side of the listing
                info_box = page.locator('div[data-type="overview"] li')
                for li in info_box.element_handles():
                    label_el = li.query_selector('div')
                    if label_el is None:
                        continue
                    label = label_el.inner_text().strip().lower()
                    text = li.inner_text().strip()
                    value = text[len(label_el.inner_text()):].strip()

                    if 'salary' in label:
                        item['salary'] = normalize_text(value)
                    if 'location' in label:
                        item['location'] = normalize_text(value)

                #gradcracker serves two different page templates - the older one uses
                #"description mb20", a newer one uses "job-description mb20"
                description = page.locator('div.description.mb20, div.job-description.mb20')
                item['description'] = description.first.inner_text(timeout=5000).strip()

                #company name is stored after the 5th backslash in the url
                url_parts = job['URL'].split('/')
                if len(url_parts) <= 5:
                    print(f"skipping {job['URL']!r}: unexpected url shape")
                    continue
                item['company_name'] = url_parts[5].replace('-', '').title()

                #doesnt add to the database
                if any(value is None for value in item.values()):
                    continue

                add_job_listing(item)
            except Exception as e:

                print(f"skipping {job['URL']!r}: failed to scrape ({e})")
                continue
    finally:
        browser.close()

def run_scrape_gradcracker(discipline, job_type, headless=True):
    with sync_playwright() as playwright:
        scrape_gradcracker(playwright, discipline=discipline, job_type=job_type, headless=headless)

#here for testing purpose to see where the scraper gets stuck
if __name__ == "__main__":
    run_scrape_gradcracker(discipline='computing-technology', job_type='internship', headless=False)

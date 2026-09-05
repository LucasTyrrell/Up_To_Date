from patchright.sync_api import sync_playwright
import time

from clean_data import normalize_text, parse_salary, map_role_type, dedupe_by_url


def scrape_gradcracker(playwright, disipline, job_type):
    #initiate the browser
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir='C:\\playwright',
        channel='chrome',
        headless=False,
        no_viewport=True,
    )

    #initiate page
    page = browser.new_page()

    #temp variables
    page_count = 1
    jobs = []

    role_type = map_role_type(job_type)

    if job_type == 'placement' or job_type == 'internship':
        job_type = 'work-placements-internships'

    while page_count < 5:

        #setting delay as to avoid sending too many requests
        time.sleep(2)

        page.goto(f'https://www.gradcracker.com/search/{disipline}/{job_type}?page={page_count}')

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

            item['Title'] = title_el.strip()
            item['URL'] = href if href.startswith('http') else "https://www.gradcracker.com" + href

            jobs.append(item)

        page_count += 1

    jobs = dedupe_by_url(jobs)

    all_jobs = []

    #deep search into each job listing
    for job in jobs:

        page.goto(job['URL'])

        time.sleep(2)

        item = {}
        item['Title'] = normalize_text(job['Title'])
        item['URL'] = job['URL']
        #item['description'] = None
        item['location'] = None
        item['salary'] = None
        item['company_name'] = None
        item['role_type'] = role_type
        item['source'] = 'gradcracker'

        #grabs all information from the info box on the side od the listing
        info_box = page.locator('div[data-type="overview"] li')
        for li in info_box.element_handles():
            label_el = li.query_selector('div')
            if label_el is None:
                continue
            label = label_el.inner_text().strip().lower()
            text = li.inner_text().strip()
            value = text[len(label_el.inner_text()):].strip()
            print(text)

            if 'salary' in label:
                item['salary'] = normalize_text(value)
            if 'location' in label:
                item['location'] = normalize_text(value)

        #company name is stored after the 5th backslash in the url

        item['company_name'] = job['URL'].split('/')[5].replace('-', '').title()

        all_jobs.append(item)



    browser.close()

    return all_jobs

with sync_playwright() as playwright:
    jobs = scrape_gradcracker(playwright, disipline='computing-technology', job_type='internship')

    print(jobs)
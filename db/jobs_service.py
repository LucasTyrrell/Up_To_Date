from db.session import get_session, get_engine_from_env
from db.jobs import JobListing, JobApplication, CV
import uuid
from urllib.parse import urlparse
from pypdf import PdfReader

#returns the currently stored urls
def get_urls():
    with get_session(get_engine_from_env()) as session:
        stored_urls = session.query(JobListing.url).all()

    urls = {row.url for row in stored_urls}
    return urls

#adds a new JobListing object to the table
def add_job_listing(listing: dict):
    #generate unique id
    id = uuid.uuid4()

    new_listing = JobListing(id=id,
                             url=listing['URL'],
                             company_name=listing['company_name'],
                             role_title=listing['title'],
                             salary=listing['salary'],
                             description=listing['description'],
                             relevance_score=None,
                             positives=None,
                             negatives=None,
                             job_location=listing['location'],
                             role_type=listing['role_type'],
                             source=listing['source'])

    with get_session(get_engine_from_env()) as session:
        session.add(new_listing)
        session.commit()


def add_job_application(listing_id):
    application_id = uuid.uuid4()
    new_application = JobApplication(application_id, listing_id)
    with get_session(get_engine_from_env()) as session:
        session.add(new_application)
        session.commit()


#returns every stored job listing as plain dicts (detached from the session)
def get_all_job_listings():
    with get_session(get_engine_from_env()) as session:
        listings = session.query(JobListing).all()

        applied_listings = {row.listing_id for row in session.query(JobApplication.listing_id)}

        unapplied_listings = []

        #filters out listings that have already been applied too
        for listing in listings:
            if listing.id not in applied_listings:
                unapplied_listings.append(listing)
        return [
            {
                "id": listing.id,
                 "url": listing.url,
                 "company_name": listing.company_name,
                 "role_title": listing.role_title,
                 "salary": listing.salary,
                 "description": listing.description,
                 "job_location": listing.job_location,
                 "role_type": listing.role_type,
                 "job_source": listing.job_source,
                 "job_relevance_score": listing.job_relevance_score,
                 "positives": listing.positives,
                 "negatives": listing.negatives,
             }
            for listing in unapplied_listings
        ]

#returns every stored job application joined with its listing, as plain dicts
def get_all_applications():
    with get_session(get_engine_from_env()) as session:
        rows = (
            session.query(JobApplication, JobListing)
            .join(JobListing, JobApplication.listing_id == JobListing.id)
            .order_by(JobApplication.date_applied.desc())
            .all()
        )
        return [
            {
                "application_id": application.application_id,
                "listing_id": listing.id,
                "company_name": listing.company_name,
                "role_title": listing.role_title,
                "description": listing.description,
                "job_location": listing.job_location,
                "role_type": listing.role_type,
                "url": listing.url,
                "date_applied": application.date_applied,
                "application_status": application.application_status,
                "interview_prep_pdf": application.interview_prep_pdf,
            }
            for application, listing in rows
        ]

def store_interview_prep_pdf(application_id, pdf_bytes):
    with get_session(get_engine_from_env()) as session:
        application = session.query(JobApplication).filter(JobApplication.application_id == application_id).first()
        if application:
            application.interview_prep_pdf = pdf_bytes
            session.commit()

def get_interview_prep(application_id):
    with get_session(get_engine_from_env()) as session:
        application = session.query(JobApplication).filter(JobApplication.application_id == application_id).first()
        return application.interview_prep_pdf if application else None

#only allows one cv to be stored
def store_cv(cv_pdf):
    reader = PdfReader(cv_pdf)
    cv_bytes = cv_pdf.getvalue()
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    with get_session(get_engine_from_env()) as session:
        exisiting = session.query(CV).first()
        if exisiting:
            exisiting.cv_text = text
            exisiting.cv = cv_bytes
        else:
            id = uuid.uuid4()
            cv = CV(id, cv_bytes, text)
            session.add(cv)

        session.commit()

def get_job_by_id(listing_id):
    with get_session(get_engine_from_env()) as session:
        listing = session.query(JobListing).filter(JobListing.id == listing_id).first()
        session.expunge_all()
        return listing

def get_listing_relevance_score(listing_id):
    with get_session(get_engine_from_env()) as session:
        listing = session.query(JobListing).filter(JobListing.id == listing_id).first()
        return listing.job_relevance_score if listing else None

def get_cv_content():
    with get_session(get_engine_from_env()) as session:
        cv = session.query(CV).first()
        return cv.cv_text if cv else None

def get_cv_pdf():
    with get_session(get_engine_from_env()) as session:
        cv = session.query(CV).first()
        return cv.cv if cv else None
#applied_listings = {row.listing_id for row in session.query(JobApplication.listing_id)}

#returns jobs listings that have not yet been scored
def get_jobs_to_score():
    with get_session(get_engine_from_env()) as session:
        unscored_listings = session.query(JobListing).filter(JobListing.job_relevance_score.is_(None)).all()
        session.expunge_all()

    return unscored_listings

def store_relevance_score(listing_id, score, positives, negatives):
    with get_session(get_engine_from_env()) as session:
        listing = session.query(JobListing).filter(JobListing.id == listing_id).first()
        if listing:
            listing.job_relevance_score = score
            listing.positives = positives
            listing.negatives = negatives


#allows user to track a job application without having scraped a listing first
def add_job_application_from_scratch(url, company_name, role_title, salary, job_location, role_type):
    #no dedicated scraper to name the source, so the listing's domain is used instead (e.g. "linkedin.com")
    source = urlparse(url).netloc.removeprefix('www.')

    listing_id = uuid.uuid4()
    listing = JobListing(
        id=listing_id, url=url, company_name=company_name, role_title=role_title,
        salary=salary, description=None, relevance_score=None,
        positives=None, negatives=None, job_location=job_location,
        role_type=role_type, source=source,
    )
    application = JobApplication(uuid.uuid4(), listing_id)

    with get_session(get_engine_from_env()) as session:
        session.add(listing)
        session.flush()
        session.add(application)
        session.commit()
from db.session import get_session, get_engine_from_env
from db.jobs import JobListing, JobApplication
import uuid

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


def get_job_listing():
    return

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
                 "job_location": listing.job_location,
                 "role_type": listing.role_type,
                 "job_source": listing.job_source,
             }
            for listing in unapplied_listings
        ]


def get_job_application():
    return

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
                "job_location": listing.job_location,
                "role_type": listing.role_type,
                "url": listing.url,
                "date_applied": application.date_applied,
                "application_status": application.application_status,
            }
            for application, listing in rows
        ]
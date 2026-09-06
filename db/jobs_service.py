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


def add_job_application():
    return

def get_job_listing():
    return

def get_job_application():
    return
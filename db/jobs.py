from sqlalchemy import ForeignKey, Column, Integer, String, CheckConstraint, DateTime, UUID
from datetime import datetime
from sqlalchemy.orm import declarative_base
import uuid
Base = declarative_base()


class JobListing(Base):
    __tablename__ = 'job_listings'

    id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column('url', String, unique=True, nullable=False)
    company_name = Column('company', String)
    role_title = Column('role_title', String)
    salary = Column('salary', String)
    job_location = Column('job_location', String)
    role_type = Column('role_type', String, CheckConstraint("role_type IN ('graduate', 'internship', 'apprenticeship')"))
    job_source = Column('job_source', String)


    def __init__(self, id, url, company_name, role_title, salary, job_location, role_type, source):
        self.id = id
        self.url = url
        self.company_name = company_name
        self.role_title = role_title
        self.salary = salary

        self.job_location = job_location
        self.role_type = role_type
        self.job_source = source


    def __repr__(self):
        return f"({self.id} {self.company_name} {self.salary} {self.description} {self.job_location} {self.role_type})"

class JobApplication(Base):
    __tablename__ = 'job_applications'
    application_id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column('listing_id', UUID(as_uuid=True), ForeignKey('job_listings.id'), default=uuid.uuid4)
    date_applied = Column('date_applied', DateTime)
    application_status = Column('application_status', String, CheckConstraint("application_status IN ('pending', 'rejected', 'successful', 'ghosted')"))

    def __init__(self, application_id, job_id):
        self.application_id = id
        self.listing_id = job_id
        self.date_applied = datetime.now()
        self.application_status = 'pending'

    def __repr__(self):
        return f"({self.application_id} {self.listing_id} {self.date_applied} {self.application_status})"
from sqlalchemy import ForeignKey, Column, Integer, String, CheckConstraint, DateTime
from datetime import datetime
from session import Base


class JobListing(Base):
    __tablename__ = 'job_listings'

    id = Column('id', Integer, primary_key=True)
    url = Column('url', String, unique=True, nullable=False)
    company_name = Column('company', String)
    role_title = Column('role_title', String)
    salary = Column('salary', Integer)
    description = Column('description', String)
    job_location = Column('job_location', String)
    role_type = Column('role_type', String, CheckConstraint("role_type IN ('graduate', 'internship', 'apprenticeship')"))

    def __init__(self, id, url, company_name, role_title, salary, description, job_location, role_type):
        self.id = id
        self.url = url
        self.company_name = company_name
        self.role_title = role_title
        self.salary = salary
        self.description = description
        self.job_location = job_location
        self.role_type = role_type

    def __repr__(self):
        return f"({self.id} {self.company_name} {self.salary} {self.description} {self.job_location} {self.role_type})"

class JobApplication(Base):
    __tablename__ = 'job_applications'
    application_id = Column('id', Integer, primary_key=True, )
    listing_id = Column('listing_id', Integer, ForeignKey('job_listings.id'))
    date_applied = Column('date_applied', DateTime)
    job_id = Column('job_id', Integer, ForeignKey('job_listings.id'))
    application_status = Column('application_status', String, CheckConstraint("application_status IN ('pending', 'rejected', 'successful', 'ghosted)"))

    def __init__(self, application_id, job_id):
        self.application_id = id
        self.listing_id = job_id
        self.date_applied = datetime.now()
        self.application_status = 'pending'

    def __repr__(self):
        return f"({self.application_id} {self.listing_id} {self.date_applied} {self.application_status})"
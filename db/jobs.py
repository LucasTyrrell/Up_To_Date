from sqlalchemy import ForeignKey, Column, Integer, String, CheckConstraint, DateTime, UUID, LargeBinary, JSON
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
    description = Column('description', String)
    job_relevance_score = Column('relevance_score', Integer)
    positives = Column('positives', JSON)
    negatives = Column('negatives', JSON)
    job_location = Column('job_location', String)
    role_type = Column('role_type', String, CheckConstraint("role_type IN ('graduate', 'internship', 'apprenticeship')"))
    job_source = Column('job_source', String)


    def __init__(self, id, url, company_name, role_title, salary, description, relevance_score, positives, negatives, job_location, role_type, source):
        self.id = id
        self.url = url
        self.company_name = company_name
        self.role_title = role_title
        self.salary = salary
        self.description = description
        self.job_relevance_score = relevance_score
        self.positives = positives
        self.negatives = negatives
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
    interview_prep_pdf = Column('interview_prep_pdf', LargeBinary)

    def __init__(self, application_id, job_id):
        self.application_id = application_id
        self.listing_id = job_id
        self.date_applied = datetime.now()
        self.application_status = 'pending'
        self.interview_prep_pdf = None

    def __repr__(self):
        return f"({self.application_id} {self.listing_id} {self.date_applied} {self.application_status})"

#just for storing the users cv to generate relevance score
class CV(Base):
    __tablename__ = 'cv'

    id = Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv = Column('cv', LargeBinary)
    cv_text = Column('cv_text', String)

    def __init__(self, id, cv_bytes, cv_text):
        self.id = id
        self.cv = cv_bytes
        self.cv_text = cv_text

    def __repr__(self):
        return f"({self.id}, {self.cv})"
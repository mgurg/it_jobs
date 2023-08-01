import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import DATE
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(sa.VARCHAR(length=36), autoincrement=False, nullable=True)
    title = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    street = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    city = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    country_code = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True)
    address_text = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    marker_icon = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True)
    workplace_type = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True)
    company_name = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    company_url = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    company_size = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    experience_level = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    latitude = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True)
    longitude = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True)
    published_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    remote_interview = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    employment_types = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    skills = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    remote = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    offer_id = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    offer_details = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    created_at = sa.Column(DATE(), autoincrement=False, nullable=True)
    updated_at = sa.Column(DATE(), autoincrement=False, nullable=True)
    ended_at = sa.Column(DATE(), autoincrement=False, nullable=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = sa.create_engine(sqlite_url, echo=False)

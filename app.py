import json
import uuid as uuid
from datetime import date, datetime, time
from pathlib import Path
from random import randint
from time import sleep
from typing import Optional

import requests
from dotenv import dotenv_values
from pydantic import EmailStr, Json
from sqlmodel import (
    JSON,
    Column,
    Field,
    Relationship,
    Session,
    SQLModel,
    String,
    create_engine,
    select,
)


def get_uuid() -> uuid.uuid4:
    """Generate SQLModel safe UUID (without leading zero), https://github.com/tiangolo/sqlmodel/pull/26"""

    value = uuid.uuid4().hex
    if value[0] == "0":
        value.replace("0", str(randint(0, 9)), 1)

    value = str(randint(0, 9)) * (32 - len(value)) + value

    return value


class Jobs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(max_length=255)
    street: Optional[str] = Field(max_length=255)
    city: Optional[str] = Field(max_length=255)
    country_code: Optional[str] = Field(max_length=16)
    address_text: Optional[str] = Field(max_length=255)
    marker_icon: Optional[str] = Field(max_length=16)
    workplace_type: Optional[str] = Field(max_length=16)
    company_name: Optional[str] = Field(max_length=255)
    company_url: Optional[str] = Field(max_length=255)
    company_size: Optional[str] = Field(max_length=255)
    experience_level: Optional[str] = Field(max_length=255)
    latitude: Optional[str] = Field(max_length=16)
    longitude: Optional[str] = Field(max_length=16)
    published_at: Optional[datetime]
    remote_interview: Optional[bool]
    employment_types: Optional[str]
    skills: Optional[str]
    remote: Optional[bool]
    offer_id: Optional[str] = Field(max_length=255)
    offer_details: Optional[str]
    created_at: Optional[datetime]
    ended_at: Optional[datetime]
    updated_at: Optional[datetime]
    # uuid: Optional[uuid.UUID]

    class Config:
        arbitrary_types_allowed = True


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_jobs():
    config = dotenv_values(".env")
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    r = requests.get(config["URL"], headers=headers)

    file = "jobs_" + date.today().isoformat() + ".json"
    filepath = Path(Path.cwd() / "offers" / file)
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(r.json(), f)


def get_job_details(id: str) -> str:
    config = dotenv_values(".env")
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    print(config["URL"] + "/" + id)
    sleep(randint(1, 2))
    r = requests.get(config["URL"] + "/" + id, headers=headers)

    return json.dumps(r.json())


def create_jobs():
    file = "jobs_" + date.today().isoformat() + ".json"
    filepath = Path(Path.cwd() / "offers" / file)

    with filepath.open() as f:
        obj = json.load(f)

    cnt = 0
    for job in obj:
        cnt += 1
        iteration = f"{cnt}/{len(obj)}"
        if cnt % 10 == 0:
            print(iteration, job["title"], job["id"])

        with Session(engine) as session:
            existing_job = session.exec(select(Jobs).where(Jobs.offer_id == job["id"])).one_or_none()

            if existing_job:
                # print("UPDATE " + job["title"])
                update_package = {
                    "ended_at": datetime.utcnow(),
                }

                for key, value in update_package.items():
                    setattr(existing_job, key, value)
                # existing_job.ended_at == datetime.utcnow()
                session.add(existing_job)
                session.commit()
                session.refresh(existing_job)
                continue

        # print(job["title"])
        job = Jobs(
            title=job["title"],
            street=job["street"],
            city=job["city"],
            country_code=job["country_code"],
            address_text=job["address_text"],
            marker_icon=job["marker_icon"],
            workplace_type=job["workplace_type"],
            company_name=job["company_name"],
            company_url=job["company_url"],
            company_size=job["company_size"],
            experience_level=job["experience_level"],
            latitude=job["latitude"],
            longitude=job["longitude"],
            published_at=job["published_at"],
            remote_interview=job["remote_interview"],
            employment_types=json.dumps(job["employment_types"]),
            skills=json.dumps(job["skills"]),
            remote=job["remote"],
            offer_id=job["id"],
            offer_details=get_job_details(job["id"]),
            created_at=datetime.utcnow(),
            ended_at=None,
            updated_at=None,
            # uuid=get_uuid(),
        )

        with Session(engine) as session:
            session.add(job)

            session.commit()


def main():
    # create_db_and_tables()
    get_jobs()
    create_jobs()


if __name__ == "__main__":
    main()

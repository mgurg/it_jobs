import json
import uuid as uuid
from datetime import date, datetime
from pathlib import Path
from random import randint
from time import sleep

import requests
from dotenv import dotenv_values
from sqlmodel import Field, Session, SQLModel, create_engine, select


def get_uuid() -> uuid.uuid4:
    """Generate SQLModel safe UUID (without leading zero), https://github.com/tiangolo/sqlmodel/pull/26"""

    value = uuid.uuid4().hex
    if value[0] == "0":
        value.replace("0", str(randint(0, 9)), 1)

    value = str(randint(0, 9)) * (32 - len(value)) + value

    return value


class Jobs(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str | None = Field(max_length=255)
    street: str | None = Field(max_length=255)
    city: str | None = Field(max_length=255)
    country_code: str | None = Field(max_length=16)
    address_text: str | None = Field(max_length=255)
    marker_icon: str | None = Field(max_length=16)
    workplace_type: str | None = Field(max_length=16)
    company_name: str | None = Field(max_length=255)
    company_url: str | None = Field(max_length=255)
    company_size: str | None = Field(max_length=255)
    experience_level: str | None = Field(max_length=255)
    latitude: str | None = Field(max_length=16)
    longitude: str | None = Field(max_length=16)
    published_at: datetime | None
    remote_interview: bool | None
    employment_types: str | None
    skills: str | None
    remote: bool | None
    offer_id: str | None = Field(max_length=255)
    offer_details: str | None
    created_at: datetime | None
    ended_at: datetime | None
    updated_at: datetime | None
    # uuid: Optional[uuid.UUID]

    class Config:
        arbitrary_types_allowed = True


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, encoding="utf-8", echo=False)


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
    # print(config["URL"] + "/" + id)
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
        f"{cnt}/{len(obj)}"
        # if cnt % 10 == 0:
        #    print(iteration)

        with Session(engine) as session:
            existing_job = session.exec(select(Jobs).where(Jobs.offer_id == job["id"])).one_or_none()

            if existing_job:
                # print("UPDATE " + job["title"])
                update_package = {"ended_at": datetime.utcnow()}

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
    # get_jobs()
    # create_jobs()
    ...

if __name__ == "__main__":
    main()

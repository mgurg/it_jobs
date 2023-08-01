import json
import uuid as uuid
from datetime import date
from pathlib import Path
from random import randint
from time import sleep

import requests
import typer
from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Base, Job, engine

APP_DIR = Path(__file__).parent


def get_jobs():
    config = dotenv_values(".env")
    headers: dict = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }

    file_name = "jobs_" + date.today().isoformat() + ".json"
    file_path: Path = Path(APP_DIR / "offers" / file_name)
    if not file_path.is_file():
        r = requests.get(config["URL_JJIT"], headers=headers)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(r.json(), f)

    return file_path


def get_job_details(id: str) -> str:
    config = dotenv_values(".env")
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    sleep(randint(1, 2))
    r = requests.get(config["URL"] + "/" + id, headers=headers)

    return json.dumps(r.json())


def create_jobs(file_path):
    with file_path.open() as f:
        obj = json.load(f)
    cnt = 0
    for job in obj:
        cnt += 1

        if cnt % 10 == 0:
            print(f"{cnt}/{len(obj)}")
        with Session(engine) as session:
            query = select(Job).where(Job.offer_id == job["id"])
            result = session.execute(query)
            db_job = result.scalar_one_or_none()
            if db_job:
                print("UPDATE " + job["title"])
                # {"ended_at": datetime.now()}
                continue

            _job_data = {
                "title": job["title"],
                "street": job["street"],
                "city": job["city"],
                "country_code": job["country_code"],
                "address_text": job["address_text"],
                "marker_icon": job["marker_icon"],
                "workplace_type": job["workplace_type"],
                "company_name": job["company_name"],
                "company_url": job["company_url"],
                "company_size": job["company_size"],
                "experience_level": job["experience_level"],
                "latitude": job["latitude"],
                "longitude": job["longitude"],
                "published_at": job["published_at"],
                "remote_interview": job["remote_interview"],
                "employment_types": json.dumps(job["employment_types"]),
                "skills": json.dumps(job["skills"]),
                "remote": job["remote"],
                "offer_id": job["id"],
                "offer_details": None,  # get_job_details(job["id"]),
                "created_at": None,
                "ended_at": None,
                "updated_at": None,
            }

            new_job = Job(**_job_data)
            session.add(new_job)
            session.commit()

            exit()
    #         if existing_job:
    #             # print("UPDATE " + job["title"])
    #             update_package = {"ended_at": datetime.utcnow()}
    #             for key, value in update_package.items():
    #                 setattr(existing_job, key, value)
    #             # existing_job.ended_at == datetime.utcnow()
    #             session.add(existing_job)
    #             session.commit()
    #             session.refresh(existing_job)
    #             continue
    #     # print(job["title"])
    #     job = Job(
    #         title=job["title"],
    #         street=job["street"],
    #         city=job["city"],
    #         country_code=job["country_code"],
    #         address_text=job["address_text"],
    #         marker_icon=job["marker_icon"],
    #         workplace_type=job["workplace_type"],
    #         company_name=job["company_name"],
    #         company_url=job["company_url"],
    #         company_size=job["company_size"],
    #         experience_level=job["experience_level"],
    #         latitude=job["latitude"],
    #         longitude=job["longitude"],
    #         published_at=job["published_at"],
    #         remote_interview=job["remote_interview"],
    #         employment_types=json.dumps(job["employment_types"]),
    #         skills=json.dumps(job["skills"]),
    #         remote=job["remote"],
    #         offer_id=job["id"],
    #         offer_details=get_job_details(job["id"]),
    #         created_at=datetime.utcnow(),
    #         ended_at=None,
    #         updated_at=None,
    #         # uuid=get_uuid(),
    #     )
    #     with Session(engine) as session:
    #         session.add(job)
    #         session.commit()

    # create_db_and_tables()
    # get_jobs()
    # create_jobs()


def main(init: bool = False):
    """
    Get Job offers
    """
    if init:
        print("Initializing DB...")
        Base.metadata.create_all(engine)
        print("Initializing DB...DONE")
        exit()
    print("Getting Job...")
    file_path = get_jobs()
    print("Getting Job...DONE")

    print("Parsing Job...")
    create_jobs(file_path)
    print("Parsing Job...DONE")


if __name__ == "__main__":
    typer.run(main)

import json
import uuid as uuid
from datetime import date, datetime
from pathlib import Path
from random import randint
from time import sleep

import requests
import typer
from dotenv import dotenv_values
from loguru import logger
from markdownify import markdownify as md
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Base, Job, engine

logger.add("logs/file_{time:YYYY-MM-DD}.log", format="{time} {level} {message}", level="INFO", backtrace=True,
           diagnose=True)

APP_DIR = Path(__file__).parent


def get_random_ua() -> str:
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_jobs():
    config = dotenv_values(".env")

    headers: dict = {"accept": "text/html,application/xhtml+xml,application/xml", "user-agent": get_random_ua()}

    file_name = "jobs_" + date.today().isoformat() + ".json"
    file_path: Path = Path(APP_DIR / "offers" / file_name)
    if not file_path.is_file():
        r = requests.get(config["URL_JJIT"], headers=headers)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(r.json(), f)

    return file_path


def get_job_details(job_id: str) -> dict | None:
    config = dotenv_values(".env")
    headers = {"accept": "text/html,application/xhtml+xml,application/xml", "user-agent": get_random_ua()}
    sleep(randint(1, 2))
    r = requests.get(config["URL_JJIT"] + "/" + job_id, headers=headers)

    if r.status_code != 200:
        logger.info(f"Missing Job details: {job_id}")
        return None

    response_dict = r.json()

    for key in [
        "future_consent_title",
        "future_consent",
        "information_clause",
        "custom_consent_title",
        "custom_consent",
    ]:
        if key in response_dict:
            del response_dict[key]

    return response_dict
    # return json.dumps(response_dict, sort_keys=True, ensure_ascii=False)


def create_jobs(file_path):
    with file_path.open() as f:
        daily_job_listing = json.load(f)

    with Session(engine) as session:
        for idx, job in enumerate(daily_job_listing):
            if (idx > 0) and (idx % 200 == 0):
                print(f"{idx}/{len(daily_job_listing)}")

            try:
                query = select(Job).where(Job.offer_id == job["id"])
                result = session.execute(query)
                db_job = result.scalar_one_or_none()
                if db_job:
                    update_db_record(db_job, session)
                    continue

                job_details = get_job_details(job["id"])
                if not job_details:
                    continue

                save_db_record(job, job_details, session)
            except Exception as e:
                logger.exception("Caught" + repr(e))


def update_db_record(db_job, session: Session) -> None:
    update_data = {"ended_at": datetime.now()}
    for key, value in update_data.items():
        setattr(db_job, key, value)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)


def save_db_record(job: dict, job_details: dict, session: Session) -> None:
    _job_data = {
        "uuid": uuid.uuid4().hex,
        "source": "JJIT",
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
        "published_at": datetime.strptime(job["published_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        "remote_interview": job["remote_interview"],
        "employment_types": json.dumps(job["employment_types"]),
        "skills": json.dumps(job["skills"]),
        "remote": job["remote"],
        "offer_id": job["id"],
        "offer_details": json.dumps(job_details, sort_keys=True, ensure_ascii=False),
        "offer_body_md": md(job_details["body"]),
        "created_at": datetime.utcnow(),
        "ended_at": None,
        "updated_at": None,
    }
    new_job = Job(**_job_data)
    session.add(new_job)
    session.commit()


def main(init: bool = False):
    """
    Get Job offers
    """
    if init:
        print("Initializing DB...")
        Base.metadata.create_all(engine)
        exit()
    print("Getting Job...")
    file_path = get_jobs()
    create_jobs(file_path)

    logger.info("That's it, beautiful and simple logging!")
    exit()


if __name__ == "__main__":
    typer.run(main)

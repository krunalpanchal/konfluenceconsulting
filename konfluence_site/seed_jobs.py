import json
from app.db.session import SessionLocal, Base, engine
from app.models.job import Job

Base.metadata.create_all(bind=engine)

with open("sample_jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

db = SessionLocal()
try:
    for item in jobs:
        db.add(Job(**item))
    db.commit()
    print(f"Inserted {len(jobs)} jobs.")
finally:
    db.close()

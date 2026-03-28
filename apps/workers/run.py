from __future__ import annotations

import time

from chronic_agent.platform.db import SessionLocal
from chronic_agent.platform.repositories import PatientRepository, WorkerRepository
from chronic_agent.features.reminders.service import ReminderService


def main():
    while True:
        with SessionLocal() as db:
            WorkerRepository(db).beat('reminder_worker')
            for patient in PatientRepository(db).list_all():
                ReminderService(db, patient.id).generate_today()
        time.sleep(60)


if __name__ == '__main__':
    main()

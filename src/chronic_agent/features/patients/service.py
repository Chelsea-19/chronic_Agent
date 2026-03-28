from __future__ import annotations

from sqlalchemy.orm import Session

from chronic_agent.core.contracts import FollowUpCreate, FollowUpOut, PatientCreate, PatientOut, TimelineItemOut
from chronic_agent.platform.repositories import FollowUpRepository, PatientRepository, TimelineRepository


class PatientService:
    def __init__(self, db: Session):
        self.patient_repo = PatientRepository(db)
        self.db = db

    def create_patient(self, payload: PatientCreate) -> PatientOut:
        row = self.patient_repo.create(**payload.model_dump())
        return PatientOut.model_validate(row, from_attributes=True)

    def list_patients(self) -> list[PatientOut]:
        return [PatientOut.model_validate(r, from_attributes=True) for r in self.patient_repo.list_all()]

    def get_patient(self, patient_id: int) -> PatientOut:
        row = self.patient_repo.get(patient_id)
        return PatientOut.model_validate(row, from_attributes=True)

    def create_followup(self, patient_id: int, payload: FollowUpCreate) -> FollowUpOut:
        row = FollowUpRepository(self.db, patient_id).create(**payload.model_dump())
        return FollowUpOut.model_validate(row, from_attributes=True)

    def list_followups(self, patient_id: int) -> list[FollowUpOut]:
        return [FollowUpOut.model_validate(r, from_attributes=True) for r in FollowUpRepository(self.db, patient_id).list_all()]

    def timeline(self, patient_id: int) -> list[TimelineItemOut]:
        return [TimelineItemOut(**item) for item in TimelineRepository(self.db, patient_id).build()]

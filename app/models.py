from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    disease = Column(String(255), nullable=True)
    medication = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)


class ClinicalTrial(Base):
    __tablename__ = "clinical_trials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    disease = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    inclusion_criteria = Column(Text, nullable=True)
    exclusion_criteria = Column(Text, nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    status = Column(String(64), default="recruiting")

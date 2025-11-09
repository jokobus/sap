from pydantic import BaseModel, AnyUrl
from typing import Union, Literal, Optional

PresentType = Literal["Present"]
YearType = int

class Grade(BaseModel):
    value: Union[float, int]
    type: Literal["GPA", "CGPA", "PERCENTAGE", "MARKS", "OTHER"]
    scale: Union[float, int]
    description: Optional[str] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_url: Optional[AnyUrl] = None
    other_links: list[AnyUrl] = []

class Position(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_year: YearType
    end_year: Union[YearType, PresentType]
    start_month: Optional[int] = None
    end_month: Optional[int] = None
    description_points: list[str] = []

class EducationEntry(BaseModel):
    institute: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[YearType] = None
    end_year: Optional[Union[YearType, PresentType]] = None
    grade_info: Optional[Grade] = None

class Project(BaseModel):
    name: str
    description_points: list[str] = []
    link: Optional[AnyUrl] = None

class Certification(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_year: Optional[YearType] = None
    expiration_year: Optional[Union[YearType, PresentType]] = None
    credential_id: Optional[str] = None
    credential_url: Optional[AnyUrl] = None

class VolunteerEntry(BaseModel):
    role: str
    organization: str
    start_year: YearType
    end_year: Union[YearType, PresentType]
    description_points: list[str] = []

class Publication(BaseModel):
    title: str
    publisher: Optional[str] = None
    publish_year: Optional[YearType] = None
    url: Optional[AnyUrl] = None

class LinkedInProfile(BaseModel):
    name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    contact: ContactInfo = ContactInfo()
    about: Optional[str] = None
    top_skills: list[str] = []
    honors_awards: list[str] = []
    certifications: list[Certification] = []
    experience: list[Position] = []
    education: list[EducationEntry] = []
    projects: list[Project] = []
    publications: list[Publication] = []
    volunteer_experience: list[VolunteerEntry] = []
    courses: list[str] = []
    languages: list[str] = []
    recommendations_count: Optional[int] = None

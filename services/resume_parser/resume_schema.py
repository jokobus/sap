from pydantic import BaseModel, AnyUrl
from typing import Union, Literal, Optional

PresentType = Literal["Present"]
YearType = int

class Grade(BaseModel):
    value: Union[float, int]
    type: Literal["GPA", "CGPA", "PERCENTAGE", "MARKS", "OTHER"]
    scale: Union[float, int]
    description: Optional[str] = None

class Education(BaseModel):
    institute: str
    field_of_study: str
    start_year: YearType
    end_year: Union[YearType, PresentType]
    grade_info: Optional[Grade] = None

class Experience(BaseModel):
    title: str
    company: str
    start_year: YearType
    end_year: Union[YearType, PresentType]
    description_points: list[str]

class Project(BaseModel):
    name: str
    description_points: list[str]
    link: AnyUrl

class SkillCategory(BaseModel):
    category_name: str
    skills: list[str]

class Certification(BaseModel):
    name: str
    issuing_organization: str
    issue_year: YearType
    expiration_year: Union[YearType, PresentType, None] = None
    credential_id: Union[str, None] = None
    credential_url: Union[AnyUrl, None] = None

class PositionOfResponsibility(BaseModel):
    title: str
    organization: str
    start_year: YearType
    end_year: Union[YearType, PresentType]
    description_points: list[str]

class Resume(BaseModel):
    name: str
    email: str
    phone: Union[str, None] = None
    social_links: list[AnyUrl] = []
    courses: list[str] = []
    
    # Required sections
    education: list[Education]

    # Optional sections (defaulting to empty lists)
    experience: list[Experience] = [] 
    projects: list[Project] = []
    skills: list[SkillCategory] = []
    certifications: list[Certification] = []
    achievements: list[str] = []
    positions_of_responsibility: list[PositionOfResponsibility] = []
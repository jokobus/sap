from pydantic import BaseModel, RootModel
from enum import Enum
from typing import List, Literal

class ExperienceLevel(str, Enum):
    Internship = "Internship"
    EntryLevel = "Entry level"
    Associate = "Associate"
    MidSeniorLevel = "Mid-Senior level"

class JobSearchParams(BaseModel):
    keyword: str
    location: str
    experience: Literal["Internship", "Entry level", "Associate", "Mid-Senior level"]

# Root model for a list of JobSearchParams
class JobSearchList(RootModel[List[JobSearchParams]]):
    pass
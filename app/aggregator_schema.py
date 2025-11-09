from pydantic import BaseModel, Field, AnyUrl, EmailStr
from typing import Optional, List, Union, Literal
from datetime import date

# --- Type Definitions ---
PresentType = Literal["Present"]
YearType = int

# --- Core Sub-Models ---

class ContactInfo(BaseModel):
    """Unified contact information from all sources."""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = Field(None, description="Professional headline/tagline")
    summary: Optional[str] = Field(None, description="Professional summary/about section")
    
class SocialLinks(BaseModel):
    """All social and professional links."""
    linkedin: Optional[AnyUrl] = None
    github: Optional[AnyUrl] = None
    portfolio: Optional[AnyUrl] = None
    other_links: List[AnyUrl] = Field(default_factory=list)

class Grade(BaseModel):
    """Academic grade information."""
    value: Union[float, int]
    type: Literal["GPA", "CGPA", "PERCENTAGE", "MARKS", "OTHER"]
    scale: Union[float, int]
    description: Optional[str] = None

class UnifiedEducation(BaseModel):
    """
    Combines education from resume and LinkedIn.
    Uses optional fields to handle varying data completeness.
    """
    institute: str
    degree: Optional[str] = Field(None, description="Degree type (e.g., Bachelor's, Master's)")
    field_of_study: Optional[str] = None
    start_year: Optional[YearType] = None
    end_year: Optional[Union[YearType, PresentType]] = None
    start_date_raw: Optional[str] = Field(None, description="Raw date from LinkedIn (e.g., 'August 2023')")
    end_date_raw: Optional[str] = None
    grade_info: Optional[Grade] = None
    description: Optional[str] = Field(None, description="Activities, coursework, achievements")
    source: List[Literal["resume", "linkedin"]] = Field(default_factory=list, description="Data sources")

class UnifiedExperience(BaseModel):
    """
    Combines work experience from resume and LinkedIn.
    Supports multiple roles at the same company.
    """
    company: str
    title: str
    start_year: Optional[YearType] = None
    end_year: Optional[Union[YearType, PresentType]] = None
    start_date_raw: Optional[str] = Field(None, description="Raw date from LinkedIn")
    end_date_raw: Optional[str] = None
    duration_raw: Optional[str] = Field(None, description="e.g., '2 years 3 months'")
    location: Optional[str] = None
    description_points: List[str] = Field(default_factory=list)
    source: List[Literal["resume", "linkedin"]] = Field(default_factory=list)

class UnifiedProject(BaseModel):
    """
    Combines projects from GitHub, resume, and LinkedIn.
    """
    name: str
    description_points: List[str] = Field(default_factory=list)
    link: Optional[AnyUrl] = None
    start_date_raw: Optional[str] = None
    end_date_raw: Optional[str] = None
    associated_with: Optional[str] = Field(None, description="Associated organization/institution")
    technologies: List[str] = Field(default_factory=list, description="Technologies/languages used")
    github_stars: Optional[int] = None
    github_forks: Optional[int] = None
    is_github_repo: bool = False
    source: List[Literal["resume", "linkedin", "github"]] = Field(default_factory=list)

class SkillCategory(BaseModel):
    """Categorized skills from all sources."""
    category_name: str
    skills: List[str]
    source: List[Literal["resume", "linkedin", "github"]] = Field(default_factory=list)

class UnifiedCertification(BaseModel):
    """Certifications from resume and LinkedIn."""
    name: str
    issuing_organization: Optional[str] = None
    issue_year: Optional[YearType] = None
    expiration_year: Optional[Union[YearType, PresentType, None]] = None
    issue_date_raw: Optional[str] = None
    expiration_date_raw: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[AnyUrl] = None
    source: List[Literal["resume", "linkedin"]] = Field(default_factory=list)

class PositionOfResponsibility(BaseModel):
    """Leadership positions and responsibilities."""
    title: str
    organization: str
    start_year: Optional[YearType] = None
    end_year: Optional[Union[YearType, PresentType]] = None
    start_date_raw: Optional[str] = None
    end_date_raw: Optional[str] = None
    description_points: List[str] = Field(default_factory=list)
    source: List[Literal["resume", "linkedin"]] = Field(default_factory=list)

# --- Main Aggregated Profile Schema ---

class FinalSchema(BaseModel):
    """
    Universal user profile schema that aggregates data from:
    - Resume (PDF/parsed)
    - LinkedIn profile
    - GitHub profile
    
    This schema maintains source tracking and handles data variations
    across different platforms.
    """
    
    # --- Core Identity & Contact ---
    contact_info: ContactInfo
    social_links: SocialLinks
    
    # --- Professional Sections ---
    education: List[UnifiedEducation] = Field(
        default_factory=list,
        description="Education history from all sources"
    )
    
    experience: List[UnifiedExperience] = Field(
        default_factory=list,
        description="Work experience from resume and LinkedIn"
    )
    
    projects: List[UnifiedProject] = Field(
        default_factory=list,
        description="Projects from GitHub, resume, and LinkedIn"
    )
    
    skills: List[SkillCategory] = Field(
        default_factory=list,
        description="Categorized skills from all sources"
    )
    
    certifications: List[UnifiedCertification] = Field(
        default_factory=list,
        description="Certifications from resume and LinkedIn"
    )
    
    # --- Additional Sections ---
    achievements: List[str] = Field(
        default_factory=list,
        description="Awards, honors, and achievements"
    )
    
    positions_of_responsibility: List[PositionOfResponsibility] = Field(
        default_factory=list,
        description="Leadership roles and responsibilities"
    )
    
    courses: List[str] = Field(
        default_factory=list,
        description="Completed courses from all sources"
    )
    
    # --- Metadata ---
    data_sources: List[Literal["resume", "linkedin", "github"]] = Field(
        default_factory=list,
        description="Which data sources were used to build this profile"
    )
    
    last_updated: Optional[str] = Field(
        None,
        description="ISO timestamp of last profile update"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "contact_info": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "location": "San Francisco, CA",
                    "headline": "Full Stack Developer | Open Source Enthusiast"
                },
                "social_links": {
                    "linkedin": "https://linkedin.com/in/johndoe",
                    "github": "https://github.com/johndoe"
                },
                "data_sources": ["resume", "linkedin", "github"]
            }
        }
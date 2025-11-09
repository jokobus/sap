"""
Tabs package for the job finder application.
Each tab is a separate module for independent development.
"""

from .profile_tab import render_profile_tab
from .skills_tab import render_skills_tab
from .job_search_tab import render_job_search_tab
from .reach_out_tab import render_reach_out_tab

__all__ = [
    'render_profile_tab',
    'render_skills_tab',
    'render_job_search_tab',
    'render_reach_out_tab',
]

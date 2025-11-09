"""Tabs package initialization"""
from .profile_tab import (
    show_init_message,
    show_basic_info_personal,
    show_basic_info_social,
    show_cv_upload,
    show_main_decision_tree,
    show_student_questions,
    show_employee_questions,
    show_unemployed_questions,
    show_interests_block
)
from .skills_tab import (
    show_skills_block,
    show_action_selection
)
from .job_search_tab import (
    show_job_suggestions,
    show_cv_suggestions,
    show_training_recommendations
)
from .reach_out_tab import (
    show_feedback_phase
)

__all__ = [
    # Profile tab
    'show_init_message',
    'show_basic_info_personal',
    'show_basic_info_social',
    'show_cv_upload',
    'show_main_decision_tree',
    'show_student_questions',
    'show_employee_questions',
    'show_unemployed_questions',
    'show_interests_block',
    # Skills tab
    'show_skills_block',
    'show_action_selection',
    # Job search tab
    'show_job_suggestions',
    'show_cv_suggestions',
    'show_training_recommendations',
    # Reach out tab
    'show_feedback_phase',
]

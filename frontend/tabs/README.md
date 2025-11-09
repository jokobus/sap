# App Modular Structure

The application has been refactored into a modular structure for easier maintenance and independent development.

## Structure

```
app/
├── app.py                      # Main application entry point
├── aggregator.py               # Data aggregation logic
├── aggregator_schema.py        # Data schemas
└── tabs/                       # Modular tab components
    ├── __init__.py            # Package initialization
    ├── profile_tab.py         # Profile upload and parsing
    ├── skills_tab.py          # Skills analysis ("What Am I good at?")
    ├── job_search_tab.py      # Job search and scraping
    └── reach_out_tab.py       # Contact and reach out functionality
```

## Tab Modules

### 1. Profile Tab (`tabs/profile_tab.py`)
- **Purpose**: Handle profile uploads and parsing
- **Functions**:
  - `render_profile_tab()`: Main rendering function
  - `run_parse_and_save()`: Parse resume, LinkedIn, and GitHub data
- **Dependencies**: `aggregator.parse_all()`

### 2. Skills Tab (`tabs/skills_tab.py`)
- **Purpose**: Display skills analysis and recommendations
- **Functions**:
  - `render_skills_tab()`: Main rendering function
- **Status**: Placeholder for future development

### 3. Job Search Tab (`tabs/job_search_tab.py`)
- **Purpose**: Generate job queries and scrape job listings
- **Functions**:
  - `render_job_search_tab()`: Main rendering function
  - `render_job_card()`: Display individual job cards
  - `build_queries_and_run_scraper()`: Execute job search
- **Dependencies**: 
  - `services.job_scraper.main_job.extract_job_search_queries()`
  - `services.job_scraper.job_scraper.scrape_linkedin_jobs()`

### 4. Reach Out Tab (`tabs/reach_out_tab.py`)
- **Purpose**: Manage contact and outreach to recruiters
- **Functions**:
  - `render_reach_out_tab()`: Main rendering function
- **Status**: Placeholder for future development

## Session State Management

All tabs share common session state variables:
- `candidate_json`: Parsed candidate profile data
- `resume_bytes`: Uploaded resume PDF bytes
- `linkedin_bytes`: Uploaded LinkedIn PDF bytes
- `github_username`: GitHub username
- `job_queries`: Generated job search queries
- `job_results`: Scraped job listings
- `selected_job`: Currently selected job for reach out
- `active_tab`: Current active tab name

## Development Workflow

### Working on Individual Tabs

1. Navigate to the specific tab file in `app/tabs/`
2. Edit the `render_*_tab()` function
3. Test by running the main application: `streamlit run app/app.py`
4. Changes are isolated and won't affect other tabs

### Adding New Tabs

1. Create a new file in `app/tabs/` (e.g., `new_tab.py`)
2. Define a `render_new_tab()` function
3. Import in `app/tabs/__init__.py`
4. Add tab routing in `app/app.py`
5. Add tab option to sidebar radio buttons

### Best Practices

- Keep tab logic self-contained in their respective files
- Use session state for data sharing between tabs
- Import only necessary dependencies in each tab
- Add fallback logic for missing dependencies
- Document placeholder sections with TODOs

## Running the Application

```bash
# From the project root
streamlit run app/app.py
```

## Benefits of Modular Structure

1. **Parallel Development**: Multiple developers can work on different tabs simultaneously
2. **Easier Maintenance**: Changes to one tab don't affect others
3. **Better Organization**: Clear separation of concerns
4. **Simpler Testing**: Individual tabs can be tested independently
5. **Reduced Conflicts**: Fewer git merge conflicts when working in teams

## Future Enhancements

### Skills Tab
- Implement skill clustering algorithm
- Add seniority mapping
- Display suggested roles based on skills
- Show source attribution for each skill

### Reach Out Tab
- Implement recruiter extraction from job URLs
- Add message templates
- Create contact list export functionality
- Integrate with LinkedIn/email APIs

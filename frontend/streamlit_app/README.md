# Streamlit Conversational Intake Demo

This small Streamlit app guides a user through a conversational-style intake form and saves the data to a JSON file and any uploaded CV to a local folder.

Files:
- `app.py` — main Streamlit app
- `requirements.txt` — Python dependencies
- Data outputs are written to `data/outputs` and uploaded CVs to `data/uploads` inside the app folder.

How to run (PowerShell on Windows):

```pwsh
# create a virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt

# run the app
streamlit run app.py
```

Notes:
- Each field can be skipped. After pressing "Save and finish" the app writes a JSON file to `data/outputs` and copies the uploaded CV into `data/uploads`.
- The UI is styled to feel a bit like a chatbot by alternating message blocks.
- This is a demo; you can adapt field validation and storage to your needs.

import streamlit as st
import json
import os
from datetime import datetime

# --- Helpers -----------------------------------------------------------------

def ensure_dirs():
    os.makedirs("data/outputs", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json(data, prefix="submission"):
    fname = f"{prefix}_{timestamp()}.json"
    path = os.path.join("data/outputs", fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    save_name = f"cv_{timestamp()}_{uploaded_file.name}"
    path = os.path.join("data/uploads", save_name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


# Render a chat message (simple styling)
def chat_message(text, who="bot"):
    if who == "bot":
        st.markdown(f"<div style='background:#f1f3f5;padding:12px;border-radius:10px;margin:6px 0'><b>Bot</b><div style='margin-top:6px'>{text}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#e7f5ff;padding:12px;border-radius:10px;margin:6px 0;text-align:right'><b>You</b><div style='margin-top:6px'>{text}</div></div>", unsafe_allow_html=True)


# Position / Degree block renderer
def render_position_block(prefix, idx, values=None):
    # unique keys using prefix+idx
    st.text_input("Position / Degree title", key=f"{prefix}_title_{idx}", value=(values.get("title") if values else ""))
    st.text_input("Institution / Company name", key=f"{prefix}_org_{idx}", value=(values.get("org") if values else ""))
    st.date_input("Start date (can skip)", key=f"{prefix}_start_{idx}", value=(values.get("start") if values and values.get("start") else None))
    st.date_input("End date (can skip)", key=f"{prefix}_end_{idx}", value=(values.get("end") if values and values.get("end") else None))
    st.text_input("Location", key=f"{prefix}_loc_{idx}", value=(values.get("location") if values else ""))
    st.text_area("Description", key=f"{prefix}_desc_{idx}", value=(values.get("description") if values else ""))
    st.checkbox("Skip this entry", key=f"{prefix}_skip_{idx}")


# --- App --------------------------------------------------------------------

def main():
    ensure_dirs()
    st.set_page_config(page_title="Conversational Intake", layout="centered")

    st.title("Conversational Intake — Streamlit Demo")

    # Ensure session state containers
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "personal" not in st.session_state:
        st.session_state["personal"] = {}

    if "student_entries" not in st.session_state:
        st.session_state["student_entries"] = []

    if "employee_jobs" not in st.session_state:
        st.session_state["employee_jobs"] = []

    if "employee_degrees" not in st.session_state:
        st.session_state["employee_degrees"] = []

    if "cv_file" not in st.session_state:
        st.session_state["cv_file"] = None

    # Intro
    if not st.session_state["messages"]:
        st.session_state["messages"].append(("bot", "Hi! I'll guide you through some quick questions — feel free to skip any. I'll save everything to a JSON file at the end."))

    # Show transcript
    for who, text in st.session_state["messages"]:
        chat_message(text, who=who)

    st.markdown("---")

    # Personal info
    st.subheader("Personal information")
    st.info("You can skip any individual field by checking the 'Skip' box next to it.")

    col1, col2 = st.columns(2)
    with col1:
        firstname = st.text_input("First name", key="firstname")
        st.checkbox("Skip first name", key="skip_firstname")
    with col2:
        lastname = st.text_input("Last name", key="lastname")
        st.checkbox("Skip last name", key="skip_lastname")

    dob = st.date_input("Date of birth (DOB)", key="dob")
    st.checkbox("Skip DOB", key="skip_dob")

    email = st.text_input("Email address", key="email")
    st.checkbox("Skip email", key="skip_email")

    phone = st.text_input("Phone number", key="phone")
    st.checkbox("Skip phone", key="skip_phone")

    linkedin = st.text_input("LinkedIn profile (URL)", key="linkedin")
    st.checkbox("Skip LinkedIn", key="skip_linkedin")

    instagram = st.text_input("Instagram profile (URL)", key="instagram")
    st.checkbox("Skip Instagram", key="skip_instagram")

    facebook = st.text_input("Facebook profile (URL)", key="facebook")
    st.checkbox("Skip Facebook", key="skip_facebook")

    # CV upload
    st.subheader("Upload CV / Resume")
    uploaded_cv = st.file_uploader("Upload PDF CV/Resume", type=["pdf"], key="cv_upload")
    if uploaded_cv:
        st.session_state["cv_file"] = uploaded_cv
        st.success(f"CV uploaded: {uploaded_cv.name}")

    # Student or Employee selection
    st.subheader("Are you a student or an employee?")
    role = st.radio("Choose role (you can skip)", options=["Student", "Employee", "Prefer not to say"], index=2)

    # Free-form questions
    st.subheader("Tell us a bit about yourself")
    free_text = st.text_area("Free field (you can skip)", key="free_text")
    st.checkbox("Skip free text", key="skip_free_text")

    st.markdown("---")

    # Conditional sections
    if role == "Student":
        st.subheader("Student: Degrees & Experience")
        st.info("Add current/previous degrees and any working experience. Each entry can be skipped.")

        if st.button("Add degree / study entry", key="add_student_entry"):
            st.session_state["student_entries"].append({})

        # render each student entry
        for i, _ in enumerate(st.session_state["student_entries"]):
            st.markdown(f"**Entry {i+1}**")
            render_position_block("student", i)
            st.markdown("---")

        st.subheader("Working experience (if any)")
        if st.button("Add work experience entry", key="add_student_work"):
            st.session_state["student_entries"].append({})

    elif role == "Employee":
        st.subheader("Employee: Current & Previous Jobs and Degrees")

        st.info("Add current job, previous jobs and your university degrees. Each entry can be skipped.")

        if st.button("Add job", key="add_employee_job"):
            st.session_state["employee_jobs"].append({})

        for i, _ in enumerate(st.session_state["employee_jobs"]):
            st.markdown(f"**Job {i+1}**")
            render_position_block("empjob", i)
            st.markdown("---")

        st.subheader("University degrees")
        if st.button("Add degree", key="add_employee_degree"):
            st.session_state["employee_degrees"].append({})

        for i, _ in enumerate(st.session_state["employee_degrees"]):
            st.markdown(f"**Degree {i+1}**")
            render_position_block("empdeg", i)
            st.markdown("---")

    else:
        st.info("You chose not to share role details. You can still fill other fields or skip them.")

    st.markdown("---")

    # Save / Submit
    if st.button("Save and finish"):
        # compile data respecting skip flags
        data = {"meta": {"created_at": timestamp(), "role": role}}
        personal = {}
        if not st.session_state.get("skip_firstname"):
            personal["firstname"] = st.session_state.get("firstname")
        if not st.session_state.get("skip_lastname"):
            personal["lastname"] = st.session_state.get("lastname")
        if not st.session_state.get("skip_dob"):
            dob_val = st.session_state.get("dob")
            personal["dob"] = dob_val.isoformat() if dob_val else None
        if not st.session_state.get("skip_email"):
            personal["email"] = st.session_state.get("email")
        if not st.session_state.get("skip_phone"):
            personal["phone"] = st.session_state.get("phone")
        if not st.session_state.get("skip_linkedin"):
            personal["linkedin"] = st.session_state.get("linkedin")
        if not st.session_state.get("skip_instagram"):
            personal["instagram"] = st.session_state.get("instagram")
        if not st.session_state.get("skip_facebook"):
            personal["facebook"] = st.session_state.get("facebook")

        data["personal"] = personal

        if not st.session_state.get("skip_free_text"):
            data["free_text"] = st.session_state.get("free_text")

        # save cv
        cv_path = save_uploaded_file(st.session_state.get("cv_file"))
        data["cv_path"] = cv_path

        # collect repeated entries
        def collect_prefix_entries(prefix):
            entries = []
            idx = 0
            # heuristics: keep scanning until a key doesn't exist for a few steps
            # but we will scan up to 20
            for idx in range(0, 40):
                title_key = f"{prefix}_title_{idx}"
                if title_key not in st.session_state:
                    continue
                skip_key = f"{prefix}_skip_{idx}"
                if st.session_state.get(skip_key):
                    continue
                t = st.session_state.get(title_key)
                if not t:
                    # if empty, skip it too
                    continue
                entry = {
                    "title": t,
                    "org": st.session_state.get(f"{prefix}_org_{idx}"),
                    "start": None,
                    "end": None,
                    "location": st.session_state.get(f"{prefix}_loc_{idx}"),
                    "description": st.session_state.get(f"{prefix}_desc_{idx}"),
                }
                s = st.session_state.get(f"{prefix}_start_{idx}")
                e = st.session_state.get(f"{prefix}_end_{idx}")
                try:
                    entry["start"] = s.isoformat() if s else None
                    entry["end"] = e.isoformat() if e else None
                except Exception:
                    entry["start"] = s
                    entry["end"] = e
                entries.append(entry)
            return entries

        if role == "Student":
            # student entries keyed by 'student'
            student_entries = collect_prefix_entries("student")
            data["student_entries"] = student_entries
        elif role == "Employee":
            data["jobs"] = collect_prefix_entries("empjob")
            data["degrees"] = collect_prefix_entries("empdeg")

        # final save
        out_path = save_json(data, prefix="intake")
        st.success(f"Saved JSON to {out_path}")
        st.download_button("Download JSON", data=json.dumps(data, ensure_ascii=False, indent=2), file_name=os.path.basename(out_path), mime="application/json")
    st.session_state["messages"].append(("bot", "Thanks — your answers were saved. You can download the JSON file above."))
    # experimental_rerun was removed / is unavailable in some Streamlit builds.
    # We keep the success message and the download button visible without forcing a rerun.

    st.markdown("\n---\n")
    st.caption("This is a demo to show how a conversational intake could be done in Streamlit. Each field can be skipped.")


if __name__ == '__main__':
    main()

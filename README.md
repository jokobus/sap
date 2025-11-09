# 🧠 SkillMatcher

**SkillMatcher** is an AI-powered platform that analyzes a candidate’s Resume, LinkedIn, and GitHub profiles to identify skills, calculate job matching confidence scores, and help users connect with relevant job opportunities.

---

## 🚀 Features

- 📄 **Resume Parsing** using Gemini 2.5 Flash for structured outputs  
- 🔗 **LinkedIn & GitHub Data Extraction** for richer skill insights  
- 🧩 **Skill Extraction** with `flair-ner-skill` model  
- 🧠 **AI-Powered Job Matching** with confidence-based scoring  
- 💬 **Reach Out** backend feature to connect with HRs or company employees  
- 🌐 **Streamlit Web App** for a smooth and modern user experience  

---

## 🧰 Tech Stack

- **Python 3.9+**  
- **Streamlit** – Web Framework  
- **Flair** – NLP Skill Extraction  
- **Pydantic** – Schema Validation  
- **Gemini 2.5 Flash** – AI Model for Structured Outputs  

---

## ⚙️ Installation & Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/skillmatcher.git
   cd skillmatcher

2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```
or Use conda env

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the Streamlit app
```bash 

python -m streamlit run frontend/app.py
```

💡 Future Improvements

Integrate the “Reach Out” feature directly into the Streamlit UI

Add user authentication and profile saving

Support for more job platforms beyond LinkedIn
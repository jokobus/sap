# Reach Out Feature - Quick Reference

## 🚀 Quick Start

```bash
# 1. Setup
./setup_reach_out.sh

# 2. Run app
streamlit run app/app.py

# 3. Use workflow:
#    Profile Tab → Job Search Tab → Reach Out Tab
```

## 📋 Prerequisites

- ✅ Uploaded profile (resume/LinkedIn)
- ✅ Selected job from search
- ✅ GOOGLE_API_KEY in environment
- ⚠️ SERPAPI_API_KEY (optional, for better results)

## 🎯 Main Features

### 1. Extract Keywords
**What**: AI analyzes job description to find 5-8 key terms
**When**: After selecting a job
**Output**: Keywords + search query + reasoning

### 2. Search LinkedIn
**What**: Find relevant people on LinkedIn
**When**: After keyword extraction
**Output**: List of profiles with names, URLs, snippets

### 3. Generate Message
**What**: Create personalized outreach message
**When**: After finding contacts (or anytime)
**Output**: Tailored message + tips

### 4. Track Outreach
**What**: Log and manage contact history
**When**: After sending messages
**Output**: CSV export of activities

## 📊 Message Types

| Type | Length | Use Case |
|------|--------|----------|
| LinkedIn Connection | Max 300 chars | Initial contact request |
| LinkedIn Message | 400-600 chars | InMail or after connection |
| Email | 3-4 paragraphs | Formal outreach |

## 🎨 Tone Options

- **Professional**: Formal business communication
- **Friendly**: Warm but professional
- **Enthusiastic**: Energetic and passionate

## ⌨️ Keyboard Shortcuts

None currently - all interactions via clicks

## 💾 Session State Keys

```python
# Inputs
candidate_json          # Your profile
selected_job           # Current job

# Workflow data
extracted_keywords     # From keyword extraction
linkedin_search_results # From LinkedIn search
selected_contact       # Chosen profile
generated_message      # Created message
outreach_log          # Activity history
```

## 🔧 Common Issues

### "No candidate profile found"
→ Go to Profile Tab, upload resume

### "Service not available"
→ Check GOOGLE_API_KEY environment variable

### "No LinkedIn results"
→ Try fewer, more specific keywords
→ Add SERPAPI_API_KEY for better results

### Import errors
→ Run: `pip install google-genai python-dotenv requests beautifulsoup4`

## 📈 Best Practices

1. ✅ Always review and customize generated messages
2. ✅ Use extracted keywords as guidance, not gospel
3. ✅ Log outreach to avoid duplicates
4. ✅ Start with professional tone
5. ✅ Keep messages concise

## 🧪 Testing

```bash
# Run all tests
python tests/test_reach_out_workflow.py

# Test individual components
python services/keyword_extractor/keyword_extractor.py
python services/reach_out_generator/reach_out_generator.py
```

## 📚 Documentation

- `REACH_OUT_SUMMARY.md` - Complete overview
- `REACH_OUT_INTEGRATION.md` - Technical details
- `REACH_OUT_DIAGRAMS.md` - Visual guides
- `app/tabs/REACH_OUT_README.md` - User guide

## 🔗 API Keys

Get API keys:
- Google Gemini: https://aistudio.google.com/apikey
- SerpAPI: https://serpapi.com/ (optional)

Set in environment:
```bash
export GOOGLE_API_KEY="your_key"
export SERPAPI_API_KEY="your_key"
```

## 📞 Support

1. Check troubleshooting in docs
2. Run test suite
3. Review error messages
4. Check environment variables

## ⚡ Performance Tips

- Use SerpAPI for faster LinkedIn search
- Generate messages in batch if needed
- Export outreach log regularly
- Clear session state if needed (Ctrl+R in Streamlit)

## 🎬 Typical Session

```
1. Upload profile         (1 min)
2. Search jobs           (2 min)
3. Extract keywords      (5 sec)
4. Search LinkedIn       (5 sec)
5. Generate message      (7 sec)
6. Review & customize    (1 min)
7. Copy & send           (30 sec)
8. Log outreach         (5 sec)

Total: ~5 minutes per job
```

## 🔄 Workflow Loop

```
Select Job → Extract Keywords → Find Contacts
     ↑              ↓
     └── Log ← Send ← Generate Message
```

## 📋 Checklist Before Sending

- [ ] Message personalized with specific details?
- [ ] Tone appropriate for relationship level?
- [ ] Contact information verified?
- [ ] No typos or errors?
- [ ] Call-to-action clear?
- [ ] Outreach logged for tracking?

## 🎁 Tips for Success

💡 **Research first**: Look at contact's profile before sending
💡 **Be specific**: Mention exact projects or skills
💡 **Show value**: Explain how you can contribute
💡 **Keep it brief**: Respect their time
💡 **Follow up**: But not too soon (wait 1-2 weeks)

## 📊 Success Metrics

Track these in Contact Manager:
- Number of outreach activities
- Response rate
- Meeting conversion rate
- Time saved per contact

## 🛠️ Advanced Usage

### Custom Keywords
Edit extracted keywords manually if needed (future feature)

### Batch Processing
Generate messages for multiple contacts (future feature)

### A/B Testing
Try different tones/types and track results (future feature)

## 🔐 Privacy & Ethics

- ✅ Only contact publicly listed professionals
- ✅ Respect LinkedIn connection limits
- ✅ Don't spam or bulk message
- ✅ Personalize each message
- ✅ Honor opt-out requests

## 🚦 Status Indicators

- 🟢 Green: Service working normally
- 🟡 Yellow: Using fallback/degraded mode
- 🔴 Red: Service unavailable

## 📦 Dependencies

```
Required:
- google-genai (AI)
- python-dotenv (config)
- requests (HTTP)
- beautifulsoup4 (parsing)

Optional:
- serpapi (better search)
```

## 🔄 Update & Maintenance

```bash
# Update dependencies
pip install --upgrade google-genai

# Re-run tests
python tests/test_reach_out_workflow.py

# Check for new features
git pull origin main
```

---

**Last Updated**: November 9, 2025
**Version**: 1.0
**Status**: Production Ready ✅

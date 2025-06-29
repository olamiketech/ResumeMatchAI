# ResumeFit – AI Resume Optimizer 🚀

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.46%2B-orange?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

ResumeFit is an **AI-powered resume optimization web app**. Upload your resume, paste a job description, and instantly receive a matching score plus actionable suggestions to boost your chances of landing interviews (80 %+ match scores are common ✨).

---

## Table of Contents
1. [Features](#features)
2. [Architecture](#architecture)
3. [Screenshots](#screenshots)
4. [Quick Start](#quick-start)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Environment Variables](#environment-variables)
8. [Deployment](#deployment)
9. [Changelog](#changelog)
10. [Contributing](#contributing)
11. [License](#license)

---

## Features
- 📄 **Multi-format upload** – PDF, DOCX & TXT.
- 🧠 **AI analysis** – TF-IDF + cosine similarity + custom heuristics.
- ✨ **GPT-4o suggestions** – keyword gaps, skill gaps, rewrite tips, quantified achievements.
- 📊 **Match score dashboard** – similarity, keyword & skills scores.
- 💾 **History & analytics** – PostgreSQL backend stores past analyses and usage metrics.
- 🌐 **Modern UI/UX** – gradient themes, responsive layout, dark-mode friendly.

## Architecture
| Layer | Tech | Description |
|-------|------|-------------|
| Frontend | Streamlit | File upload UI, results visualisation |
| Text Processing | NLTK | Tokenisation, stopword removal, stemming |
| ML Engine | Scikit-learn | TF-IDF vectorisation & cosine similarity |
| AI Enhancements | OpenAI GPT-4o | Resume rewriting & suggestions |
| Database | PostgreSQL via SQLAlchemy | History, analytics & user sessions |

```
┌────────────┐      Upload        ┌────────────┐
│  Frontend  │ ───────────────▶ │  Text      │
│  (Streamlit)│                   │ Processing │
└────────────┘ ◀─────────────── │  & ML      │
     ▲  ▲                         └────────────┘
     │  │                              │
History │                              ▼
     │  │                        ┌────────────┐
     │  └──────────────────────▶ │  Database  │
     ▼                           └────────────┘
 Analytics
```

## Screenshots
> *Add screenshots/gifs here if available.*

## Quick Start
```bash
# 1. Clone repository
$ git clone https://github.com/<your-username>/ResumeFit.git
$ cd ResumeFit

# 2. Create virtual environment (optional but recommended)
$ python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
$ pip install -r requirements.txt  # or use the provided pyproject.toml with Poetry/UV

# 4. Download required NLTK corpora (first run only)
$ python - <<'PY'
import nltk; nltk.download("punkt"); nltk.download("stopwords")
PY

# 5. Start Streamlit
$ streamlit run ResumeMatchAI/app.py  # update path if necessary
```

## Usage
1. Upload a **PDF, DOCX, or TXT** resume.
2. Paste or type the **job description** into the text box.
3. Hit **Analyse**.
4. Review your **match score**, keyword/skills gaps and AI suggestions.
5. Iterate until you achieve an 80 %+ score – then celebrate! 🎉

## Project Structure
```
├── ResumeMatchAI/            # Main application package
│   ├── app.py                # Streamlit entry point
│   └── utils/                # Modular utilities
│       ├── pdf_extractor.py
│       ├── docx_extractor.py
│       ├── text_processor.py
│       ├── resume_analyzer.py
│       ├── openai_service.py
│       └── database.py
├── .streamlit/               # Streamlit config
├── requirements.txt / pyproject.toml
├── README.md                 # ← you are here
└── .replit / replit.md       # Replit deployment files
```

## Environment Variables
Create a `.env` file (already git-ignored) and set:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

## Deployment
### Replit (autoscale)
1. Fork the repl.
2. Set the above environment variables in the Replit Secrets tab.
3. Replit automatically installs dependencies and runs `streamlit run ...` as defined in `.replit`.

### Other hosts (Railway, Fly, etc.)
- Ensure Python 3.11, install deps, and expose port `8501` (default Streamlit port) or set `PORT` env variable.

## Changelog (excerpt)
- **2025-06-27** – Modern UI/UX revamp, AI score tuning, GPT-4o integration, PostgreSQL analytics.
- **2025-06-29** – Added comprehensive README for GitHub release.

See `replit.md` for a detailed change log.

## Contributing
Pull requests are welcome! Please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

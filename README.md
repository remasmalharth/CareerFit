# CareerFit

Compares the skills in a resume (PDF or DOCX) with the skills required by a job description, then shows what is missing and how to close each gap. Works with English and Arabic job descriptions.

**Live demo:** [add your link here] | **API docs:** [your-api-url]/docs

## Features

- Detects 70+ skills with English and Arabic aliases
- Separates **required** from **preferred** skills (preferred counts half)
- **Partial credit** for related skills (for example PyTorch when the job asks for TensorFlow)
- Optional **semantic matching** with multilingual sentence embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), restricted to concept skills (Machine Learning, Data Analysis, ...) because tool names produced false matches
- Weighted score, coverage by category, and a mini-project suggestion for every missing skill
- **REST API** (FastAPI) with automatic docs at `/docs`
- Automated tests (pytest) run by GitHub Actions on every push; Dockerfile included

## Project structure

```
matcher.py            keyword matching, required/preferred detection, scoring
semantic_matcher.py   embeddings-based matching
recommendations.py    how to close each skill gap
extractors.py         PDF/DOCX text extraction (shared)
app.py                Streamlit interface
api.py                FastAPI backend
evaluate.py           accuracy measurement
test_matcher.py       automated tests
```

## Evaluation

Skill extraction was tested on **[N]** real job descriptions (Bayt, LinkedIn, Jadarat) that I labeled by hand.

| Method   | Precision | Recall | F1   |
| -------- | --------- | ------ | ---- |
| keyword  | [X]%      | [X]%   | [X]% |
| semantic | [X]%      | [X]%   | [X]% |
| hybrid   | [X]%      | [X]%   | [X]% |

Semantic threshold chosen by testing 0.65 to 0.80: **[value]**.
Reproduce: `python evaluate.py all`

**What I learned:** [one or two honest sentences, for example where semantic matching helped and where it added false matches.]

## Run locally

```
pip install -r requirements.txt
streamlit run app.py                 # web interface
uvicorn api:app --reload             # API, then open /docs
pip install sentence-transformers    # optional, for semantic matching
pytest                               # tests
```

## Docker (API)

```
docker build -t careerfit .
docker run -p 8000:8000 careerfit
```

## Limitations

- Keyword and alias based, so unusual wording can be missed
- Semantic layer only covers concept skills and needs threshold tuning
- Scanned (image-only) PDFs are not supported

## Future work

- LLM-based skill extraction
- Larger labeled dataset and a Saudi job-market skills dashboard

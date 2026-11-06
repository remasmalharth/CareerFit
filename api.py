from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from extractors import extract_text
from matcher import analyze
 
app = FastAPI(
    title="CareerFit API",
    description="Compare a resume with a job description and get a skill match.",
    version="1.0",
)
 
 
class TextRequest(BaseModel):
    resume_text: str
    job_description: str
    use_semantic: bool = False
 
 
def run_analysis(resume_text, job_description, use_semantic):
    if not resume_text.strip():
        raise HTTPException(status_code=422, detail="No readable resume text.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is empty.")
 
    if not use_semantic:
        return analyze(resume_text, job_description)
 
    try:
        from semantic_matcher import find_skills_hybrid
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Semantic matching is not installed on this server.",
        )
 
    try:
        return analyze(resume_text, job_description, extractor=find_skills_hybrid)
    except TypeError:
        raise HTTPException(
            status_code=501,
            detail="matcher.analyze does not support the extractor option yet.",
        )
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
 
@app.post("/analyze-text")
def analyze_text(request: TextRequest):
    """Send the resume text and the job description as JSON."""
    return run_analysis(
        request.resume_text, request.job_description, request.use_semantic
    )
 
 
@app.post("/analyze")
async def analyze_file(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    use_semantic: bool = Form(False),
):
    """Upload a PDF or DOCX resume and send the job description as text."""
    data = await resume.read()
 
    try:
        resume_text = extract_text(resume.filename, data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this file.")
 
    return run_analysis(resume_text, job_description, use_semantic)
 

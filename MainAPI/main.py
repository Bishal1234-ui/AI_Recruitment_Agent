import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from agentFunctions import create_vector_store_job_details, decision_maker_chain, get_resume_text
from databaseFunction import save_result_to_db
from fastapi.middleware.cors import CORSMiddleware


# Load env
load_dotenv()
OLLAMA_SERVER = "http://localhost:11434"

# Initialize FastAPI app
app = FastAPI()

# -------------------- Setup CORS --------------------
# Allowing requests from frontend (e.g., React running at localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server react 
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# <<< TO SEND THE JOB DETAILS TO REACT FRONTEND >>>
@app.get("/get-job-details")
def get_message():
    # Hardcoded job details
    job_title = "Software Engineer Intern"
    job_details = "We are looking for a passionate Software Engineer Intern to join our dynamic team. You will work on exciting projects and gain hands-on experience in software development."
    requirements = "Currently pursuing a degree in Computer Science or related field. Basic understanding of software development principles."
    experience = "0-1 years of experience. Previous internship experience is a plus."
    skills = "JavaScript,jAVA, C++, Problem-solving"
    return {
        "job_title": job_title, "job_details": job_details, 
        "requirements":requirements, "experience":experience, "skills":skills
        }


# ---------- API Endpoint ----------
@app.post("/analyze-resume/")
async def analyze_resume(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    resume: UploadFile = File(...)
):
    # Hardcoded job details
    job_title = "Software Engineer Intern"
    job_details = "We are looking for a passionate Software Engineer Intern to join our dynamic team. You will work on exciting projects and gain hands-on experience in software development."
    requirements = "Currently pursuing a degree in Computer Science or related field. Basic understanding of software development principles."
    experience = "0-1 years of experience. Previous internship experience is a plus."
    skills = "JavaScript,jAVA, C++, Problem-solving"

    # Combine job text
    job_text = (
        f"job_title: {job_title}\n"
        f"job_details: {job_details}\n"
        f"requirements: {requirements}\n"
        f"experience: {experience}\n"
        f"skills: {skills}"
    )

    # Save uploaded resume temporarily
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await resume.read())
            resume_path = temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}")

    # Process job description
    vector_store = create_vector_store_job_details(job_text)

    # Extract resume text
    try:
        resume_text = get_resume_text(resume_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

    # Analyze
    analysis_chain = decision_maker_chain(vector_store)
    result = analysis_chain.invoke(resume_text)

    # Save to DB
    save_result_to_db(candidate_name, candidate_email, resume_path, result.decision, result.compatibility_score, result.justification)

    return JSONResponse(content={
        "decision": result.decision,
        "compatibility_score": result.compatibility_score,
        "justification": result.justification
    })

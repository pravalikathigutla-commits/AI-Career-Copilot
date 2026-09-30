from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import os
import json
import ollama

app = FastAPI()

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Career Copilot is running!"
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # -----------------------------------
    # 1. Save uploaded resume
    # -----------------------------------

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # -----------------------------------
    # 2. Extract text from PDF
    # -----------------------------------

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"

    # -----------------------------------
    # 3. AI Prompt
    # -----------------------------------

    prompt = f"""
You are an AI Career Copilot for a Computer Science student
who wants to become a Software Engineer.

Analyze ONLY the information present in the resume.

IMPORTANT:
- Do not invent skills.
- Do not invent projects.
- Do not invent certifications.
- Do not invent experience.
- Do not assume a skill just because it is common.
- Do not recommend random technologies.
- Focus on realistic Software Engineering preparation.
- Keep recommendations appropriate for an entry-level CSE student.

========================================
RESUME SCORING
========================================

Calculate the resume score using exactly these categories:

Programming Languages: 15 points
DSA / Problem Solving: 20 points
Projects: 15 points
Internship / Experience: 15 points
Core CS Fundamentals: 10 points
Database / SQL: 10 points
Development Skills: 10 points
Resume Quality: 5 points

TOTAL = 100 points

Do NOT randomly change the scoring system.

Give points based only on evidence in the resume.

========================================
CAREER FOCUS
========================================

The candidate's target is Software Engineering.

Prioritize these areas when recommending skills:

1. Java
2. Data Structures and Algorithms
3. Problem Solving
4. OOP
5. SQL
6. DBMS
7. Operating Systems
8. Computer Networks
9. Spring Boot
10. REST APIs
11. Git and GitHub
12. React
13. AI / Machine Learning projects

Do NOT recommend technologies such as
Bootstrap, jQuery, Kubernetes, Jira, etc.
unless the resume or career context strongly justifies them.

========================================
RETURN FORMAT
========================================

Return ONLY valid JSON.

Do not use markdown.

Do not use ```json.

Use EXACTLY this structure:

{{
  "score": 0,

  "score_breakdown": {{
    "programming_languages": 0,
    "dsa_problem_solving": 0,
    "projects": 0,
    "internship_experience": 0,
    "core_cs": 0,
    "database_sql": 0,
    "development_skills": 0,
    "resume_quality": 0
  }},

  "strong_skills": [],

  "missing_skills": [],

  "recommended_skills": [],

  "job_roles": [],

  "recommended_projects": [],

  "roadmap": {{
    "month_1": [],
    "month_2": [],
    "month_3": []
  }},

  "improvements": []
}}

========================================
RULES
========================================

score:
- Number between 0 and 100.
- Must equal the sum of the score_breakdown.

score_breakdown:
- programming_languages: maximum 15
- dsa_problem_solving: maximum 20
- projects: maximum 15
- internship_experience: maximum 15
- core_cs: maximum 10
- database_sql: maximum 10
- development_skills: maximum 10
- resume_quality: maximum 5

strong_skills:
Only list skills clearly shown in the resume.

missing_skills:
List important Software Engineering skills that are missing
or weak in the resume.

recommended_skills:
Give realistic next skills to learn.
Maximum 8 items.

job_roles:
Give realistic entry-level roles.
Maximum 5 items.

recommended_projects:
Give projects that improve Software Engineering skills.
Maximum 4 items.

roadmap:
Create a realistic 3-month roadmap.

Month 1 should focus on:
Java + DSA + problem solving.

Month 2 should focus on:
SQL + DBMS + OOP + backend fundamentals.

Month 3 should focus on:
Spring Boot + REST API + one strong project.

If the resume already contains one of these skills,
recommend the next appropriate level instead.

improvements:
Give practical resume improvements.
Maximum 8 items.

Keep every item short and specific.

========================================
RESUME
========================================

{resume_text}
"""

    # -----------------------------------
    # 4. Run local Qwen AI
    # -----------------------------------

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    ai_text = response["message"]["content"].strip()

    # -----------------------------------
    # 5. Remove accidental markdown
    # -----------------------------------

    if ai_text.startswith("```"):
        ai_text = ai_text.replace("```json", "")
        ai_text = ai_text.replace("```", "")
        ai_text = ai_text.strip()

    # -----------------------------------
    # 6. Convert AI response to JSON
    # -----------------------------------

    try:

        ai_analysis = json.loads(ai_text)

    except json.JSONDecodeError:

        ai_analysis = {
            "score": 0,

            "score_breakdown": {
                "programming_languages": 0,
                "dsa_problem_solving": 0,
                "projects": 0,
                "internship_experience": 0,
                "core_cs": 0,
                "database_sql": 0,
                "development_skills": 0,
                "resume_quality": 0
            },

            "strong_skills": [],

            "missing_skills": [],

            "recommended_skills": [],

            "job_roles": [],

            "recommended_projects": [],

            "roadmap": {
                "month_1": [],
                "month_2": [],
                "month_3": []
            },

            "improvements": [
                "AI returned an invalid response. Please try again."
            ]
        }

    # -----------------------------------
    # 7. Return result
    # -----------------------------------

    return {
        "filename": file.filename,
        "resume_text": resume_text,
        "ai_analysis": ai_analysis
    }
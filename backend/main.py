
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

import os
import json
import tempfile
import time


# ==========================================
# 1. Load Environment Variables
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ==========================================
# 2. Create FastAPI Application
# ==========================================

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-career-copilot-zeta-five.vercel.app",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. Allow React Frontend
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. Home Route
# ==========================================

@app.get("/")
def home():
    return {
        "message": "AI Career Copilot is running!"
    }


# ==========================================
# 5. Upload Resume
# ==========================================

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # --------------------------------------
    # Check Gemini API Key
    # --------------------------------------

    if client is None:
        return {
            "error": "Gemini API key is not configured."
        }

    # --------------------------------------
    # Check File Type
    # --------------------------------------

    if not file.filename:
        return {
            "error": "Please select a file."
        }

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Please upload a PDF resume."
        }

    # --------------------------------------
    # Read Uploaded File
    # --------------------------------------

    file_bytes = await file.read()

    if not file_bytes:
        return {
            "error": "The uploaded file is empty."
        }

    # --------------------------------------
    # Temporary File Path
    # --------------------------------------

    temp_file_path = None

    try:

        # ======================================
        # Save PDF Temporarily
        # ======================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        # ======================================
        # Extract Text From PDF
        # ======================================

        reader = PdfReader(temp_file_path)

        resume_text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                resume_text += page_text + "\n"

        resume_text = resume_text.strip()

        # ======================================
        # Check Resume Text
        # ======================================

        if not resume_text:
            return {
                "error": "Could not extract text from the PDF resume."
            }

        # ======================================
        # AI Prompt
        # ======================================

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

        # ======================================
        # Run Gemini AI With Retry
        # ======================================

        response = None

        for attempt in range(3):

            try:

                print(
                    f"Sending request to Gemini... "
                    f"Attempt {attempt + 1}/3"
                )

                response = client.models.generate_content(
                   model="gemini-3.7-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                print("Gemini response received.")

                break

            except Exception as e:

                error_message = str(e)

                print(
                    f"Gemini attempt {attempt + 1} failed: "
                    f"{error_message}"
                )

                if attempt == 2:
                    raise

                print("Retrying in 3 seconds...")

                time.sleep(3)

        # ======================================
        # Check Gemini Response
        # ======================================

        if response is None:
            return {
                "error": "Gemini did not return a response."
            }

        if not response.text:
            return {
                "error": "Gemini returned an empty response."
            }

        # ======================================
        # Get Gemini Response Text
        # ======================================

        ai_text = response.text.strip()

        # ======================================
        # Remove Accidental Markdown
        # ======================================

        if ai_text.startswith("```"):
            print("========== GEMINI RAW RESPONSE ==========")
            print(ai_text)
            print("=========================================")

            ai_text = ai_text.replace(
                "```json",
                ""
            )

            ai_text = ai_text.replace(
                "```",
                ""
            )

            ai_text = ai_text.strip()

        # ======================================
        # Convert Gemini Response To JSON
        # ======================================

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
                    "Gemini returned an invalid JSON response. Please try again."
                ]
            }

        # ======================================
        # Return Result
        # ======================================

        return {
            "filename": file.filename,
            "resume_text": resume_text,
            "ai_analysis": ai_analysis
        }

    except Exception as e:

        print(
            f"Resume analysis failed: {str(e)}"
        )

        return {
            "error": f"Resume analysis failed: {str(e)}"
        }

    finally:

        # ======================================
        # Delete Temporary File
        # ======================================

        if (
            temp_file_path
            and os.path.exists(temp_file_path)
        ):

            os.remove(temp_file_path)
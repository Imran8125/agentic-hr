import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import re

def ats_evaluate_resume(resume: str, job_description: str) -> dict:
    """
    Evaluate a resume against a job description using Gemini and return a structured JSON.
    """
    GOOGLE_API_KEY = "AIzaSyDd2r_suN_CtD355-CMckFvLRgiS1yrOQQ"
    if not GOOGLE_API_KEY:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY,
    )
    ats_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an ATS (Applicant Tracking System) assistant. Parse the candidate's resume and compare it to the job description. Return a JSON with: score (1-100), missing_skills (list), and match_summary (string). Be objective and concise. Do NOT include markdown or code block markers in your response."),
        ("human", "Resume: {resume}\nJob Description: {job_description}"),
    ])
    chain = ats_prompt | llm | StrOutputParser()
    result = chain.invoke({"resume": resume, "job_description": job_description})
    import json
    # Remove markdown code block markers if present
    cleaned = re.sub(r'```[a-zA-Z]*', '', result).replace('```', '').strip()
    # Try to extract JSON substring if present
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except Exception:
        return {"score": 0, "missing_skills": [], "match_summary": "Could not parse result: " + cleaned} 
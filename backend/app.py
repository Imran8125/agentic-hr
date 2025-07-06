import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser
import ats_evaluation
import json
import re
from email.mime.text import MIMEText
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import csv
from datetime import datetime, timedelta
from googleapiclient.discovery import build as gcal_build

# --- Configuration ---
GOOGLE_API_KEY = "AIzaSyDd2r_suN_CtD355-CMckFvLRgiS1yrOQQ"
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "imran8122k05@gmail.com")

# --- LLM Setup ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY,
)

# --- Memory ---
memory = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="input",
    return_messages=True,
)

# --- Prompts ---
initial_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent interview agent. You will be given a candidate's resume and a job description. Generate an initial interview question that is relevant to both. Be specific and insightful."),
    ("human", "Resume: {resume}\nJob Description: {job_description}\n"),
])

followup_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an adaptive interview agent. Given the conversation so far, the candidate's resume, and the job description, generate the next best follow-up question. Be specific and insightful. Avoid repeating previous questions."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Resume: {resume}\nJob Description: {job_description}\nLast Answer: {last_answer}"),
])

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert interviewer. Based on the conversation, the candidate's resume, and the job description, provide a structured summary with the following fields: Technical Score (1-10), Behavioral Fit (1-10), Overall Fit (1-10), and a small brief Recommendation. Format as JSON with keys: technical_score, behavioral_fit, overall_fit, recommendation."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Resume: {resume}\nJob Description: {job_description}"),
])

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email_via_gmail(to_email, subject, body):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw}
    print(f"Sending email to {to_email} with subject: {subject}")
    service.users().messages().send(userId='me', body=message_body).execute()

# --- Interview Loop ---
def interview_loop(resume, job_description, num_questions=5):
    chat_history = []
    # Initial question
    initial_chain = initial_prompt | llm | StrOutputParser()
    question = initial_chain.invoke({"resume": resume, "job_description": job_description, "input": ""})
    for i in range(num_questions):
        print(f"\nInterviewer: {question}")
        answer = input("Candidate: ")
        chat_history.append(("human", question))
        chat_history.append(("ai", answer))
        memory.save_context({"input": question}, {"output": answer})
        # Generate next question
        followup_chain = followup_prompt | llm | StrOutputParser()
        question = followup_chain.invoke({
            "resume": resume,
            "job_description": job_description,
            "last_answer": answer,
            "chat_history": memory.load_memory_variables({"input": ""})["chat_history"],
            "input": answer,
        })
    # Summary
    summary_chain = summary_prompt | llm | StrOutputParser()
    summary = summary_chain.invoke({
        "resume": resume,
        "job_description": job_description,
        "chat_history": memory.load_memory_variables({"input": ""})["chat_history"],
        "input": "",
    })
    print("\n--- Interview Summary ---")
    print(summary)
    return summary

def parse_interview_summary(summary):
    # Remove markdown code block markers if present
    cleaned = re.sub(r'```[a-zA-Z]*', '', summary).replace('```', '').strip()
    # Try to extract JSON substring if present
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        cleaned = match.group(0)
    try:
        parsed = json.loads(cleaned)
        # Only keep the required fields
        return {
            "technical_score": parsed.get("technical_score", ""),
            "behavioral_fit": parsed.get("behavioral_fit", ""),
            "recommendation": parsed.get("recommendation", "")
        }
    except Exception:
        return {"technical_score": "", "behavioral_fit": "", "recommendation": cleaned}

def is_candidate_selected(ats_score, technical_score):
    try:
        ats_score = float(ats_score)
        technical_score = float(technical_score)
        return ats_score >= 7 and technical_score >= 7
    except Exception:
        return False

def create_calendar_event(candidate_name, candidate_email, start_time):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES + ['https://www.googleapis.com/auth/calendar'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = gcal_build('calendar', 'v3', credentials=creds)
    end_time = start_time + timedelta(minutes=30)
    event = {
        'summary': f'Interview with {candidate_name}',
        'description': f'Interview for candidate {candidate_name} ({candidate_email})',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': candidate_email}],
    }
    created_event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
    return created_event.get('htmlLink', '')

def process_candidate(candidate, interview_start_time, job_description):
    candidate_name = candidate['name']
    candidate_email = candidate['email']
    resume = candidate['resume']

    # ATS Evaluation
    ats_result = ats_evaluation.ats_evaluate_resume(resume, job_description)
    print(f"\n--- ATS Evaluation for {candidate_name} ---")
    print(ats_result)

    # Generate unique interview link for Flask frontend
    # Assume the frontend is hosted at FRONTEND_URL
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    import hashlib
    token = hashlib.sha256(f"{candidate_email}{candidate_name}".encode()).hexdigest()[:16]
    event_link = f"{FRONTEND_URL}/interview/{token}"

    # Send interview invitation email with event link
    interview_info_subject = "Interview Invitation - Agentic HR"
    interview_info_body = f"""
Dear {candidate_name},

Thank you for your application. We are pleased to invite you to the next stage of our hiring process: a chat-based interview. Please be prepared to answer questions related to your experience and the job description you applied for.

Your interview is scheduled for: {interview_start_time.strftime('%Y-%m-%d %H:%M UTC')}
Join using this link: {event_link}

Best regards,
Agentic HR Team
"""
    try:
        print(f"Sending email to {candidate_email} with subject: {interview_info_subject}")
        send_email_via_gmail(candidate_email, interview_info_subject, interview_info_body)
        print(f"Interview invitation email sent to {candidate_email}")
    except Exception as e:
        print(f"Failed to send interview invitation email: {e}")

    # Interview
    summary = interview_loop(resume, job_description)
    interview_json = parse_interview_summary(summary)

    # Save to JSON file
    json_file = "results.json"
    result_entry = {
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "ats_score": ats_result.get("score", ""),
        "ats_missing_skills": ats_result.get("missing_skills", []),
        "ats_match_summary": ats_result.get("match_summary", ""),
        "interview_technical_score": interview_json.get("technical_score", ""),
        "interview_behavioral_fit": interview_json.get("behavioral_fit", ""),
        "interview_recommendation": interview_json.get("recommendation", ""),
    }
    if os.path.isfile(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []
    data.append(result_entry)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved to {json_file}")

    # Send result email to candidate (no evaluation details)
    selected = is_candidate_selected(ats_result.get('score', 0), interview_json.get('technical_score', 0))
    result_subject = "Your Interview Result - Agentic HR"
    if selected:
        result_body = f"""
Dear {candidate_name},

Congratulations! You have been selected to proceed to the next stage of our hiring process. We will contact you soon with further details.

Best regards,
Agentic HR Team
"""
    else:
        result_body = f"""
Dear {candidate_name},

Thank you for participating in our interview process. After careful consideration, we regret to inform you that you have not been selected to proceed further at this time. We appreciate your interest and encourage you to apply again in the future.

Best regards,
Agentic HR Team
"""
    try:
        send_email_via_gmail(candidate_email, result_subject, result_body)
        print(f"Result email sent to {candidate_email}")
    except Exception as e:
        print(f"Failed to send result email: {e}")

    # Send admin/HR notification with evaluation details
    admin_subject = f"Candidate Evaluation: {candidate_name}"
    admin_body = f"""
Candidate Name: {candidate_name}
Candidate Email: {candidate_email}

ATS Evaluation:
Score: {ats_result.get('score', '')}
Missing Skills: {', '.join(ats_result.get('missing_skills', []))}
Match Summary: {ats_result.get('match_summary', '')}

Interview Evaluation:
Technical Score: {interview_json.get('technical_score', '')}
Behavioral Fit: {interview_json.get('behavioral_fit', '')}
Recommendation: {interview_json.get('recommendation', '')}

Selected: {'Yes' if selected else 'No'}
"""
    try:
        send_email_via_gmail(ADMIN_EMAIL, admin_subject, admin_body)
        print(f"Admin/HR notification sent to {ADMIN_EMAIL}")
    except Exception as e:
        print(f"Failed to send admin/HR notification: {e}")

# --- Main ---
if __name__ == "__main__":
    print("=== Agentic HR Batch Processing ===\n")
    # Read job description from file
    with open("job_description.txt", "r", encoding="utf-8") as f:
        job_description = f.read()
    # Read candidates from CSV
    candidates = []
    with open("candidates.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            candidates.append(row)
    # Start interviews from now, each 1 hour apart
    start_time = datetime.utcnow() + timedelta(minutes=5)
    for i, candidate in enumerate(candidates):
        interview_time = start_time + timedelta(hours=i)
        print(f"\nProcessing candidate {candidate['name']} (Interview at {interview_time.strftime('%Y-%m-%d %H:%M UTC')})")
        process_candidate(candidate, interview_time, job_description) 
from flask import Flask, request, render_template_string, redirect, url_for
import os
import uuid
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
import ats_evaluation
from app import initial_prompt, followup_prompt, summary_prompt, llm, memory, parse_interview_summary, is_candidate_selected
from langchain.schema import StrOutputParser

app = Flask(__name__)

# In-memory storage for demo (replace with DB in production)
candidate_links = {}
candidate_status = {}
CANDIDATE_STATE_FILE = 'candidates_state.json'

# Modern CSS and Bootstrap
MODERN_CSS = '''
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        margin: 0;
        padding: 20px;
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 15px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        text-align: center;
    }
    .header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
    }
    .content {
        padding: 40px;
    }
    .upload-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 30px;
        margin-bottom: 30px;
        border: 2px dashed #dee2e6;
        text-align: center;
    }
    .upload-section:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-control {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 12px 15px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .form-control:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .table thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .table th {
        border: none;
        padding: 15px;
        font-weight: 600;
    }
    .table td {
        padding: 15px;
        border-bottom: 1px solid #f1f3f4;
    }
    .table tbody tr:hover {
        background: #f8f9fa;
    }
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    .status-completed {
        background: #d4edda;
        color: #155724;
    }
    .interview-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    .interview-link:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    .chat-message {
        margin-bottom: 15px;
        padding: 12px 16px;
        border-radius: 10px;
        max-width: 80%;
    }
    .chat-interviewer {
        background: #667eea;
        color: white;
        margin-left: auto;
        margin-right: 0;
    }
    .chat-candidate {
        background: #e9ecef;
        color: #333;
        margin-right: auto;
        margin-left: 0;
    }
    .chat-input {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        padding: 15px 20px;
        font-size: 16px;
        width: 100%;
        margin-bottom: 15px;
    }
    .chat-input:focus {
        border-color: #667eea;
        outline: none;
    }
    .btn-send {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 30px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .btn-send:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .completion-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 18px;
        font-weight: 600;
    }
</style>
'''

ADMIN_TEMPLATE = MODERN_CSS + '''
<div class="container">
    <div class="header">
        <h1>🤖 Agentic HR Dashboard</h1>
        <p>Intelligent Recruitment Management System</p>
    </div>
    <div class="content">
        <div class="upload-section">
            <h3>📁 Upload Files & Start Batch Processing</h3>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label><strong>Job Description (txt):</strong></label><br>
                    <input type="file" name="job_description" class="form-control" accept=".txt" required>
                </div>
                <div class="form-group">
                    <label><strong>Candidates (CSV):</strong></label><br>
                    <input type="file" name="candidates" class="form-control" accept=".csv" required>
                </div>
                <button type="submit" class="btn-primary">🚀 Upload & Start Batch</button>
            </form>
        </div>
        
        <h2>👥 Candidate Status</h2>
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Interview Link</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in candidates %}
                    <tr>
                        <td><strong>{{c['name']}}</strong></td>
                        <td>{{c['email']}}</td>
                        <td><span class="status-badge status-{{c['status'].lower()}}">{{c['status']}}</span></td>
                        <td>{% if c['link'] %}<a href="{{c['link']}}" class="interview-link" target="_blank">🔗 Start Interview</a>{% endif %}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
'''

INTERVIEW_TEMPLATE = MODERN_CSS + '''
<div class="container">
    <div class="header">
        <h1>🎯 Interview Session</h1>
        <p>Candidate: {{name}}</p>
    </div>
    <div class="content">
        <div class="chat-container">
            {% for q, a in chat %}
            <div class="chat-message chat-interviewer">
                <strong>Interviewer:</strong> {{q}}
            </div>
            <div class="chat-message chat-candidate">
                <strong>You:</strong> {{a}}
            </div>
            {% endfor %}
        </div>
        
        {% if not finished %}
        <form method="post">
            <div class="chat-message chat-interviewer">
                <strong>Interviewer:</strong> {{question}}
            </div>
            <input type="text" name="answer" class="chat-input" autofocus required placeholder="Type your answer here...">
            <button type="submit" class="btn-send">📤 Send Answer</button>
        </form>
        {% else %}
        <div class="completion-message">
            ✅ Interview Complete! Thank you for your time.
        </div>
        {% endif %}
    </div>
</div>
'''

def load_candidate_state():
    if os.path.exists(CANDIDATE_STATE_FILE):
        with open(CANDIDATE_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_candidate_state(state):
    with open(CANDIDATE_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global candidate_links, candidate_status
    if request.method == 'POST':
        # Save uploaded files
        job_desc = request.files['job_description']
        candidates_csv = request.files['candidates']
        job_desc.save('job_description.txt')
        candidates_csv.save('candidates.csv')
        # Parse candidates and generate links
        import csv
        candidate_links = {}
        candidate_status = {}
        state = {}
        with open('candidates.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                token = str(uuid.uuid4())
                candidate_links[row['email']] = token
                candidate_status[row['email']] = {'name': row['name'], 'email': row['email'], 'status': 'Pending', 'link': url_for('interview', token=token, _external=True)}
                state[token] = {
                    'name': row['name'],
                    'email': row['email'],
                    'resume': row['resume'],
                    'chat': [],
                    'finished': False
                }
        save_candidate_state(state)
        return redirect(url_for('admin'))
    candidates = list(candidate_status.values())
    return render_template_string(ADMIN_TEMPLATE, candidates=candidates)

@app.route('/interview/<token>', methods=['GET', 'POST'])
def interview(token):
    state = load_candidate_state()
    cand = state.get(token)
    if not cand:
        return "Invalid interview link.", 404
    # Load job description
    with open('job_description.txt', 'r', encoding='utf-8') as f:
        job_description = f.read()
    chat = cand.get('chat', [])
    finished = cand.get('finished', False)
    # Interview logic
    if not chat:
        # First question
        initial_chain = initial_prompt | llm | StrOutputParser()
        question = initial_chain.invoke({"resume": cand['resume'], "job_description": job_description, "input": ""})
    else:
        if finished:
            question = None
        else:
            last_answer = chat[-1][1]
            followup_chain = followup_prompt | llm | StrOutputParser()
            question = followup_chain.invoke({
                "resume": cand['resume'],
                "job_description": job_description,
                "last_answer": last_answer,
                "chat_history": [
                    {"role": "human", "content": q} if i % 2 == 0 else {"role": "ai", "content": a}
                    for i, (q, a) in enumerate(chat)
                ],
                "input": last_answer,
            })
    if request.method == 'POST' and not finished:
        answer = request.form['answer']
        chat.append((question, answer))
        cand['chat'] = chat
        # For demo, limit to 3 questions
        if len(chat) >= 3:
            cand['finished'] = True
            finished = True
        state[token] = cand
        save_candidate_state(state)
        if finished:
            # Optionally, trigger backend evaluation here
            pass
        return redirect(url_for('interview', token=token))
    name = cand['name']
    return render_template_string(INTERVIEW_TEMPLATE, name=name, chat=chat, question=question, finished=finished)

@app.route('/')
def home():
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True) 
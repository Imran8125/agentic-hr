# 🤖 Agentic HR AI - Intelligent Recruitment Platform

An end-to-end automated recruitment system that leverages AI to streamline the hiring process. Built with LangChain, Gemini AI, and modern web technologies.

## ✨ Features

### 🎯 Core Capabilities
- **AI-Powered Resume Screening (ATS)** - Automatically evaluates resumes against job descriptions
- **Adaptive Chat Interviews** - Dynamic, AI-driven interviews that adapt based on candidate responses
- **Automated Email Communication** - Sends interview invitations and results via Gmail API
- **Modern Web Interface** - Professional HR dashboard and candidate interview portal
- **Batch Processing** - Handle multiple candidates simultaneously
- **Result Storage & Analytics** - JSON-based data storage with export capabilities

### 🚀 Key Benefits
- **Time Savings** - Automate repetitive HR tasks
- **Consistency** - Standardized evaluation process
- **Scalability** - Handle large candidate pools efficiently
- **Candidate Experience** - Professional, interactive interview process
- **Data-Driven Decisions** - Comprehensive evaluation metrics

## 🛠️ Technology Stack

- **Backend**: Python, LangChain, Google Gemini 1.5 Flash
- **Frontend**: Flask, HTML5, CSS3, JavaScript
- **APIs**: Google Gmail API, Google Calendar API
- **Data Storage**: JSON files (extensible to databases)
- **Authentication**: OAuth 2.0 with Google APIs

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Gmail API credentials
- Gemini API key

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/agentic-hr-ai.git
cd agentic-hr-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Google APIs

#### Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API: **APIs & Services > Library > Gmail API > Enable**
4. Create OAuth credentials: **APIs & Services > Credentials > Create Credentials > OAuth client ID**
5. Choose **Desktop application** as application type
6. Download the JSON file and rename it to `credentials.json`
7. Place it in the `backend/` directory

#### Gemini API Setup
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set environment variable:
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### 4. Configure Environment Variables
```bash
export ADMIN_EMAIL="admin@yourcompany.com"
export FRONTEND_URL="http://localhost:5000"
```

## 📁 Project Structure

```
AgenticHR/
├── backend/
│   ├── app.py                 # Main backend application
│   ├── ats_evaluation.py      # ATS evaluation module
│   ├── credentials.json       # Google OAuth credentials
│   ├── candidates.csv         # Sample candidate data
│   └── job_description.txt    # Sample job description
├── frontend/
│   └── app.py                 # Flask web application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

## 🎯 Usage

### 1. Start the Backend (Batch Processing)
```bash
cd backend
python app.py
```

### 2. Start the Frontend (Web Interface)
```bash
cd frontend
python app.py
```

### 3. Access the HR Dashboard
Open your browser and go to: `http://localhost:5000/admin`

### 4. Upload Files
- Upload a job description (`.txt` file)
- Upload a candidates CSV file with columns: `name`, `email`, `resume`

### 5. Monitor Candidates
- View candidate status in the dashboard
- Share interview links with candidates
- Monitor interview progress

## 📊 Sample Data Format

### Candidates CSV (`candidates.csv`)
```csv
name,email,resume
John Doe,john.doe@email.com,"Detail-oriented software engineer with 3 years of experience in Python development..."
Jane Smith,jane.smith@email.com,"Full-stack developer with 4 years of experience in JavaScript, React, and Node.js..."
```

### Job Description (`job_description.txt`)
```
Job Title: Junior Python Developer

Description:
We are seeking a Junior Python Developer to join our backend team...

Responsibilities:
- Develop and maintain backend services using Python and Flask
- Optimize code for performance and scalability
- Work closely with frontend developers and participate in code reviews

Requirements:
- 1+ years of experience with Python
- Familiarity with Flask and SQL
- Good communication and teamwork skills
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Gemini API key
- `ADMIN_EMAIL`: Email address for admin notifications
- `FRONTEND_URL`: URL where the frontend is hosted

### Customization
- Modify interview questions in `backend/app.py`
- Adjust ATS scoring criteria in `backend/ats_evaluation.py`
- Customize email templates in the backend code
- Update UI styling in `frontend/app.py`

## 🔒 Security Considerations

- Keep `credentials.json` secure and never commit it to version control
- Use environment variables for sensitive data
- Implement proper authentication for production use
- Consider rate limiting for API calls
- Regular security audits of dependencies

## 🚀 Deployment

### Local Development
```bash
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && python app.py
```

### Production Deployment
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up proper SSL certificates
- Configure environment variables
- Use a production database (PostgreSQL, MongoDB)
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the code comments and this README
- **Community**: Join our discussions in GitHub Discussions

## 🔮 Roadmap

- [ ] Firebase integration for cloud storage
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app for candidates
- [ ] Integration with job boards
- [ ] Advanced scheduling with calendar integration
- [ ] Video interview capabilities
- [ ] AI-powered candidate matching

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- UI inspired by modern SaaS applications

---

**Made with ❤️ for modern HR teams** 
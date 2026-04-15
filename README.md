===> AI Email Prioritizer & Automation

===> AI-powered system that intelligently classifies and prioritizes emails using NLP and secure Gmail integration.

===> Overview

Managing emails efficiently is a common challenge in both personal and professional environments. This project solves that by automatically analyzing incoming emails and categorizing them based on urgency, intent, and context.

It integrates with Gmail using OAuth 2.0 and leverages advanced Natural Language Processing (NLP) models to deliver structured, real-time insights.

🔗 Live Demo: https://email-prioritizer-email-spam-detector.onrender.com/

✨ Key Features
🔐 Secure Gmail integration using OAuth 2.0
📥 Fetch and process real-time emails via Gmail API
🧠 AI-powered classification using BART-Large-MNLI
⚡ Fast inference (<2 seconds per batch)
📊 Categorization based on urgency and intent
🌐 REST API-based microservice architecture
☁️ Cloud deployment (Render)
🏗️ System Architecture

User → OAuth Authentication → Gmail API → Email Fetching  

→ NLP Model (BART) → Classification → Structured Output (JSON)

===> Tech Stack
🔹 Backend
Python
FastAPI
🔹 AI / NLP
Hugging Face Transformers
BART-Large-MNLI
🔹 APIs & Authentication
Google OAuth 2.0
Gmail API
🔹 Deployment
Render (Cloud Hosting)
🔹 Tools
Git & GitHub
Postman (API Testing)
⚙️ How It Works

1️⃣ User authenticates via Google OAuth
2️⃣ System securely fetches emails using Gmail API
3️⃣ Emails are processed using NLP model
4️⃣ Model classifies emails into categories:
Urgent
Needs Reply
Informational

5️⃣ Results are returned as structured JSON
===> API Endpoints
Method	Endpoint	Description
GET	/auth	Authenticate user via Google OAuth
GET	/emails	Fetch user emails
POST	/classify	Classify email content
===> Sample Output
{
  "email": "Meeting scheduled at 5 PM",
  "category": "Urgent",
  "confidence": 0.92
}
===> Project Structure
email-prioritizer/
│── app/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── utils/
│
│── requirements.txt
│── README.md


⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/Arun979321/email-prioritizer-oauth.git
cd email-prioritizer-oauth

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Setup Environment Variables

Create a .env file:

GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
REDIRECT_URI=your_redirect_url

4️⃣ Run Application
uvicorn app.main:app --reload
===> Usage
Authenticate using /auth
Fetch emails via /emails
Classify emails using /classify

📈 Performance Optimization
⚡ Reduced model latency to <2 seconds per batch
🧠 Efficient model caching and memory handling
📉 Optimized API response time
🔮 Future Improvements
📊 Frontend dashboard for visualization
📧 Support for multiple email providers
🧠 Model fine-tuning for higher accuracy
🔔 Real-time notifications
🤝 Contribution

 <img width="1872" height="877" alt="image" src="https://github.com/user-attachments/assets/4694b8eb-3669-4723-8cef-e476a4ed5e4a" />

Contributions are welcome!
Feel free to fork this repository and submit a pull request.

===> Author

Arun Kumar
📧 arunntw2004@gmail.com

🔗 GitHub: https://github.com/Arun979321

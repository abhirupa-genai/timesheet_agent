# Timesheet Agent 🤖

A modular AI-powered agent for generating and managing task-wise breakdown reports from Frappe/ERPNext.

## 📂 Project Structure##
timesheet_app/
├── main.py              # Application entry point
├── src/
│   ├── processor/       # FastAPI Backend (Data handling & Excel/CSV generation)
│   └── bot/             # Streamlit Frontend (Chat UI & User interaction)
├── .env                 # API Credentials (Ignored by Git)


### 1. Environment Setup
Create a `.env` file in the root directory and add your Frappe credentials:
```env
FRA_URL=[https://your-hrms-link.com](https://your-hrms-link.com)
API_KEY=your_api_key
API_SECRET=your_api_secret

Create .streamlit/secrets.toml for Google OAuth(Local Only):
[google_oauth]
client_id = "your_id"
client_secret = "your_secret"


# Timesheet Agent 

A modular AI-powered agent for generating and managing task-wise breakdown reports from Frappe/ERPNext.

##  Project Structure
timesheet_agent/
├── main.py              # Application entry point
├── src/
│   ├── processor/       # FastAPI Backend (Data handling & PDF/CSV generation)
│   └── bot/             # Streamlit Frontend (Chat UI & User interaction)
├── data/                # Container for collecting resource files from HRMS
├── report/              # Output container for generated reports
├── .env                 # API Credentials (Ignored by Git)

### Environment Setup
Create a `.env` file in the root directory and add your Frappe credentials:
```env
FRA_URL=[https://your-hrms-link.com](https://your-hrms-link.com)
API_KEY=your_api_key
API_SECRET=your_api_secret

Create .streamlit/secrets.toml for Google OAuth (Local only):
[google_oauth]
client_id = "your_id"
client_secret = "your_secret"

### Running the Application
Start the backend (FastAPI):
uvicorn src.processor.rest:app --reload
Start the frontend (Streamlit):
streamlit run src/bot/chat_ui.py




from readfiles import read_excel, read_csv
from initialize_chat import initialize, genarate_response, transform_history
import datetime
from google import genai
import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()


#User authentication
CLIENT_ID = st.secrets["google_oauth"]["CLIENT_ID"]
CLIENT_SECRET = st.secrets["google_oauth"]["CLIENT_SECRET"]
ALLOWED_DOMAIN = st.secrets["google_oauth"]["ALLOWED_DOMAIN"]

# Standard OAuth URLs
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"
REDIRECT_URI = "http://localhost:8501/"
#REDIRECT_URI = "http://localhost:8501/oauth2callback"
SCOPE = "openid email profile"


oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, None, None)

# Initialize session state for the user email if it doesn't exist
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# If we don't have an email yet, show the login flow
if st.session_state["user_email"] is None:
    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        key="google_auth",
    )
    
    # Check if Google sent back the data
    if result and "token" in result:
        # Some versions of streamlit-oauth return 'token' as a string or dict
        # Let's extract the access token correctly
        if isinstance(result["token"], dict):
            access_token = result["token"].get("access_token")
        else:
            # If the library returns the token directly
            access_token = result["token"]

        # Fetch the email from Google's API
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        
        # PERSIST THE EMAIL
        st.session_state["user_email"] = user_info.get("email")
        
        # Force a rerun to exit this IF block and move to the chat
        st.rerun()
    else:
        st.stop() # Wait here until the user clicks login

# --- EVERYTHING BELOW THIS IS THE CHAT INTERFACE ---
# If we reached here, st.session_state["user_email"] is no longer None

email = st.session_state["user_email"]


# Domain Check
if not email.endswith(f"@{ALLOWED_DOMAIN}"):
    st.error(f"Access denied for {email}.")
    if st.button("Log out"):
        st.session_state["user_email"] = None
        st.rerun()
    st.stop()

st.success(f"Authenticated: {email}")
# --- YOUR CHATBOT CODE STARTS HERE ---

# ---- Chat starts with initialization ---
if "initialized" not in st.session_state:

    # Place your one-time setup here:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    df_report = pd.read_excel("Timesheet_Report.xlsx")
    df_report_csv = df_report.to_csv(index=False)
    print(df_report.shape)

    #Retrieve the start and end date from the chat
    
    """st.write("Select the report duration:")
    #col1, col2 = st.columns(2)
    #with col1 :
        start_date = st.date_input("Start Date (YYYY-MM-DD) :", datetime.date.today())
    with col2:
        end_date = st.date_input("End Date (YYYY-MM-DD) :", datetime.date.today() )

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    initial_history = initialize(start_str, end_str)
    """
    st.session_state["messages"].append({
        "role": "assistant", 
        "content": f"{df_report_csv}"
    })
    
    st.session_state["initialized"] = True
    st.session_state["start_time"] = datetime.date.today()
    
    # If you have a heavy model or database connection:
    # st.session_state["my_model"] = load_heavy_model()
    
    print("Initialization complete!") 



st.title("NstarX Timesheet Chatbot")

# Display chat messages from history on app rerun
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask something..."):

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    user_prompt = transform_history(st.session_state['messages']) + "\n" + email+ "\n" + prompt
    
    # Create a placeholder for the bot's response
    response = genarate_response(user_prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    #print(st.session_state.messages)

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.getenv("API_URL", "http://localhost:5000/chat")

# App title and description
st.title("AI Chat Assistant")
st.subheader("Frontend Interface")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Display assistant thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Prepare chat history for API request
            messages = [{"role": m["role"], "content": m["content"]} 
                       for m in st.session_state.messages]
            
            # Call backend API
            response = requests.post(
                API_URL,
                json={
                    "messages": messages,
                    "temperature": st.session_state.get("temperature", 0.7)
                }
            )
            
            if response.status_code == 200:
                assistant_response = response.json().get("response", "")
                message_placeholder.markdown(assistant_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                message_placeholder.markdown(f"Error: API returned status code {response.status_code}")
            
        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")

# Sidebar with settings
with st.sidebar:
    st.header("Settings")
    st.write("Configure your chat assistant:")
    
    # API URL input
    api_url = st.text_input("API URL", value=API_URL)
    if api_url and api_url != API_URL:
        API_URL = api_url
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        key="temperature",
        help="Higher values make output more random, lower values make it more deterministic."
    )
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Frontend powered by Streamlit") 
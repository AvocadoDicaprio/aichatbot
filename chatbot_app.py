import streamlit as st
import requests
import json

# Configuration
# Configuration
# 1. Open a new terminal and run: ngrok http 11434
# 2. Copy the "Forwarding" URL (starts with https://)
# 3. Paste it below:
OLLAMA_URL = "https://juana-nonforeclosing-rufus.ngrok-free.dev/api/chat"
MODEL = "gpt-oss:20b"

st.set_page_config(page_title="GPT-OSS Chatbot", page_icon="🤖")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🤖 GPT-OSS Chatbot")
st.caption(f"Powered by {MODEL} running locally via Ollama")

# Custom CSS to float the clear button at the bottom left
st.markdown("""
    <style>
    /* Target the container of the generic stButton */
    div.stButton > button {
        position: fixed;
        bottom: 28px; /* Lower it to align with input box */
        left: 15px;
        z-index: 9999;
        background-color: #ff4b4b;
        color: white;
        border-radius: 50%; /* Circle shape */
        width: 40px; /* Small fixed width */
        height: 40px; /* Small fixed height */
        padding: 0;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        background-color: #ff6b6b;
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("🗑️"):
    st.session_state.messages = []
    st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare the payload for Ollama
        payload = {
            "model": MODEL,
            "messages": st.session_state.messages,
            "stream": True 
        }
        
        try:
            # Add User-Agent to look like a browser, and the skip-warning header
            headers = {
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with requests.post(OLLAMA_URL, json=payload, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    st.error(f"Status Code: {response.status_code}")
                    st.error(f"Response Text: {response.text}") # Show us the HTML/Error body
                
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line)
                        if "message" in body and "content" in body["message"]:
                            content_chunk = body["message"]["content"]
                            full_response += content_chunk
                            message_placeholder.markdown(full_response + "▌")
                        
                        if body.get("done", False):
                            break
                            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {e}")
        except Exception as e:
            st.error(f"General Error: {e}")

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

st.title("🤖 GPT-OSS Chatbot")
st.caption(f"Powered by {MODEL} running locally via Ollama")

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
            with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
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
            
        except Exception as e:
            st.error(f"Error connecting to Ollama: {e}")

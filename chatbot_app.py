import streamlit as st
import requests
import json
from duckduckgo_search import DDGS

# Configuration
# Configuration
# 1. Open a new terminal and run: ngrok http 11434
# 2. Copy the "Forwarding" URL (starts with https://)
# 3. Paste it below:
OLLAMA_URL = "https://juana-nonforeclosing-rufus.ngrok-free.dev/api/chat"
MODEL = "gpt-oss:20b"

st.set_page_config(page_title="GPT-OSS Chatbot", page_icon="🤖")

# Initialize chat history and search state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "enable_search" not in st.session_state:
    st.session_state.enable_search = False

st.title("🤖 GPT-OSS Chatbot")
st.caption(f"Powered by {MODEL} running locally via Ollama")

# Custom CSS for floating buttons
st.markdown("""
    <style>
    /* Global Base Style for Floating Buttons */
    div.stButton > button {
        position: fixed !important;
        bottom: 50px !important;
        z-index: 99999 !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        border-radius: 4px !important;
        background-color: transparent !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        box-shadow: none !important;
    }
    
    /* Hover */
    div.stButton > button:hover {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border-color: rgba(128, 128, 128, 0.5) !important;
    }

    /* LEFT BUTTON: Clear (Targeting 1st Column in the Block) */
    [data-testid="column"]:nth-of-type(1) div.stButton > button {
        position: fixed !important;
        bottom: 50px !important;
        left: calc(50% - 215px) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* RIGHT BUTTON: Search (Targeting 3rd Column in the Block) */
    [data-testid="column"]:nth-of-type(3) div.stButton > button {
        position: fixed !important;
        bottom: 50px !important;
        left: auto !important;
        right: auto !important;
        left: calc(50% + 180px) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Mobile Responsive Logic */
    @media (max-width: 768px) {
        [data-testid="column"]:nth-of-type(1) div.stButton > button {
            left: 10px !important;
            bottom: 60px !important;
        }
        [data-testid="column"]:nth-of-type(3) div.stButton > button {
            left: auto !important;
            right: 10px !important;
            bottom: 60px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Render buttons in separate columns to ensure DOM separation logic applies cleanly
# An invisible container at the top
c1, c2, c3 = st.columns([1, 10, 1])

with c1:
    if st.button("🗑️", key="btn_clear", help="Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with c3:
    search_icon = "🌐" if not st.session_state.enable_search else "✅"
    if st.button(search_icon, key="btn_search", help="Toggle Search"):
        st.session_state.enable_search = not st.session_state.enable_search
        st.rerun()

# Highlight Active Search State (Targeting the 3rd column button)
if st.session_state.enable_search:
    st.markdown("""
    <style>
    [data-testid="column"]:nth-of-type(3) div.stButton > button {
        border-color: #4CAF50 !important;
        color: #4CAF50 !important;
        background-color: rgba(76, 175, 80, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize chat history (fallback)
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
        
        # Prepare messages for payload (copy to avoid modifying display)
        payload_messages = list(st.session_state.messages)
        
        # Web Search Logic
        if st.session_state.enable_search:
            with st.spinner("Searching the web..."):
                try:
                    results = DDGS().text(prompt, max_results=3)
                    if results:
                        context_str = "\n".join([f"- **{r['title']}**: {r['body']} ({r['href']})" for r in results])
                        
                        # Augment the last message with context
                        last_msg = payload_messages[-1]
                        new_content = f"STRICT INSTRUCTION: You are a truthful assistant. Answer the user's question ONLY using the provided Search Results below. Do NOT use your own prior knowledge. If the answer is not explicitly contained in the results, you MUST simply say 'I cannot find the answer in the provided search results.'\n\nSearch Results:\n{context_str}\n\nUser Question: {last_msg['content']}"
                        payload_messages[-1] = {"role": "user", "content": new_content}
                except Exception as e:
                    st.error(f"Search Error: {e}")

        # Prepare the payload for Ollama
        payload = {
            "model": MODEL,
            "messages": payload_messages,
            "stream": True,
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

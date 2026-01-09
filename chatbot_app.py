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
    /* Common style for floating buttons */
    .floating-button {
        position: fixed;
        bottom: 50px;
        z-index: 9999;
        background-color: transparent;
        color: inherit;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 4px;
        width: 38px;
        height: 38px;
        font-size: 20px;
        padding: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: none;
    }
    
    /* Hover effect */
    .floating-button:hover {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.4);
    }
    
    /* Specific positioning */
    /* Clear Button (Left) */
    .clear-btn {
        left: calc(50% - 400px);
    }
    
    /* Search Button (Right of Clear Button) */
    .search-btn {
        left: calc(50% - 355px); /* Spaced 45px to the right of clear btn */
    }
    
    /* Active state for search button */
    .search-active {
        background-color: rgba(0, 255, 0, 0.1) !important;
        border: 1px solid rgba(0, 255, 0, 0.5) !important;
        color: #00AA00 !important;
    }

    /* Mobile adjustments */
    @media (max-width: 767px) {
        .clear-btn { left: 5px; bottom: 50px; }
        .search-btn { left: 50px; bottom: 50px; }
    }
    </style>
    """, unsafe_allow_html=True)

# 1. Clear Button (Using visible label as ID effectively, wrapped in a div for positioning)
# Streamlit buttons are hard to style individually without unique keys or containers. 
# We will use columns to hack the position or just render them standard and use JS/CSS targeting.
# Actually, the easiest way to CSS target specific buttons in Streamlit is using the specific element index usually, 
# but that's brittle.
# A robust way is to use empty container/html hack, OR just rely on "key" arguments and some luck.
# Better yet: Let's use `st.columns` inside a container if possible? No, we need them fixed.

# New Approach: 
# We just render two buttons. Streamlit buttons render as `div.row-widget.stButton`.
# We can use the `key` to identify them? No, keys don't appear in DOM.
# We will use the nth-of-type selector in CSS.
# First button = Clear. Second button = Search.

st.markdown("""
<style>
/* First button (Clear) */
div.stButton:nth-of-type(1) > button {
    position: fixed;
    bottom: 50px;
    z-index: 9999;
    background-color: transparent;
    color: inherit;
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 4px;
    width: 38px;
    height: 38px;
    font-size: 20px;
    padding: 0 !important;
    left: calc(50% - 400px); /* Desktop Default */
}

/* Second button (Search) - Positioned on the RIGHT side of the input box */
div.stButton:nth-of-type(2) > button {
    position: fixed;
    bottom: 50px;
    z-index: 9999;
    background-color: transparent;
    color: inherit;
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 4px;
    width: 38px;
    height: 38px;
    font-size: 20px;
    padding: 0 !important;
    left: calc(50% + 360px); /* Mirroring the left side (approx 720px gap between buttons) */
}

/* Hover effects */
div.stButton > button:hover {
    background-color: rgba(128, 128, 128, 0.1);
    border: 1px solid rgba(128, 128, 128, 0.4);
}

/* Mobile Overrides */
@media (max-width: 767px) {
    div.stButton:nth-of-type(1) > button { left: 5px; } /* Bin Left */
    div.stButton:nth-of-type(2) > button { left: auto; right: 5px; } /* Search Right */
}
</style>
""", unsafe_allow_html=True)

# Render buttons
# Button 1: Clear
if st.button("🗑️", help="Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Button 2: Search Toggle
search_icon = "🌐" if not st.session_state.enable_search else "✅"
if st.button(search_icon, help="Toggle Web Search"):
    st.session_state.enable_search = not st.session_state.enable_search
    st.rerun()

# Apply active style conditionally if search is on
if st.session_state.enable_search:
    st.markdown("""
    <style>
    div.stButton:nth-of-type(2) > button {
        border: 1px solid #4CAF50 !important;
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
        if enable_search:
            status_container = st.status("Searching the web...", expanded=False)
            try:
                results = DDGS().text(prompt, max_results=3)
                if results:
                    context_str = "\n".join([f"- **{r['title']}**: {r['body']} ({r['href']})" for r in results])
                    status_container.markdown(context_str)
                    status_container.update(label="Search completed!", state="complete", expanded=False)
                    
                    # Augment the last message with context
                    last_msg = payload_messages[-1]
                    new_content = f"Answer the user's question using the following search results as context if relevant. If the results are not relevant, answer normally.\n\nSearch Results:\n{context_str}\n\nUser Question: {last_msg['content']}"
                    payload_messages[-1] = {"role": "user", "content": new_content}
                else:
                    status_container.update(label="No results found.", state="complete")
            except Exception as e:
                status_container.update(label="Search failed", state="error")
                st.error(f"Search Error: {e}")

        # Prepare the payload for Ollama
        payload = {
            "model": MODEL,
            "messages": payload_messages,
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

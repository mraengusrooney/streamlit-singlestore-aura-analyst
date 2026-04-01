import streamlit as st
import requests
import json
import sseclient # Make sure you ran: pip install sseclient-py

API_URL = "https://apps.us-east-1.cloud.singlestore.com/v1/organizations/<org-id>/projects/<project-id>f/analyst/chat"
API_URL = "https://apps.us-east-1.cloud.singlestore.com/v1/organizations/1bf54b61-3069-436a-914c-7779003f0fbd/projects/d5580703-c940-4150-ba33-cc6ebdb0209f/analyst/chat"

# Please revoke this token in your SingleStore portal and use st.secrets!
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

st.set_page_config(page_title="Real Time FX Data Chatbot", layout="wide")

# ==========================================
# UI LAYOUT: Logo in the top middle
# ==========================================
# Create 3 columns. The middle one will hold the image.
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Replace this URL with your actual image link or local file path (e.g., "logo.png")
    logo_url = "https://t4.ftcdn.net/jpg/06/39/87/73/360_F_639877377_5DZI29djToo5AxYCsusmtCmyCIb7ocIP.jpg"
    # use_container_width ensures the image automatically scales to fit the middle column
    st.image(logo_url, use_container_width=True)

# Use HTML to center the title and caption to match the centered logo
st.markdown("<h1 style='text-align: center;'> Real Time Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Talk to your SingleStore-powered agent.</p>", unsafe_allow_html=True)
st.divider() # Adds a nice visual break before the chat starts
# ==========================================

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me something..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "message": prompt,
        "stream": True #  Set to True to allow real-time text streaming
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, stream=True)
        
        if response.status_code == 200:
            client = sseclient.SSEClient(response)
            full_reply = ""
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                for event in client.events():
                    if event.event == "response.output_text.delta":
                        data = json.loads(event.data)
                        full_reply += data.get("delta", "")
                        message_placeholder.markdown(full_reply + "▌")
                
                message_placeholder.markdown(full_reply)
            
            st.session_state["messages"].append({"role": "assistant", "content": full_reply})

        else:
            st.error(f"⚠️ Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"❌ Could not connect to backend: {e}")

"""
Streamlit Frontend - Phase 8.
"""
import streamlit as st
import requests
import uuid

API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Agentic Support System", page_icon="🤖", layout="wide")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"sess-{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

def chat_interface():
    st.title("🤖 Support Chat")
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("How can I help you today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Agent is thinking..."):
            try:
                response = requests.post(f"{API_BASE_URL}/chat", json={
                    "query": prompt,
                    "session_id": st.session_state["session_id"]
                })
                response.raise_for_status()
                data = response.json()
                
                reply = data["response"]
                st.chat_message("assistant").markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                with st.expander("Agent Reasoning Details", expanded=False):
                    st.write(f"**Intent:** {data['intent']} (Confidence: {data['confidence']:.2f})")
                    if data.get("requires_human_approval"):
                        st.warning(f"Human Approval Required! Ticket ID: {data['approval_id']}")
                    if data.get("escalated"):
                        st.error("Session Escalated to Human Support.")
                        
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")

def dashboard_interface():
    st.title("🛡️ Human Approval Dashboard")
    
    try:
        response = requests.get(f"{API_BASE_URL}/approvals")
        response.raise_for_status()
        approvals = response.json()
        
        if not approvals:
            st.info("No pending approvals.")
        else:
            for app in approvals:
                with st.container(border=True):
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        st.subheader(f"Ticket: {app['id']}")
                        st.write(f"**Action:** {app['action_type'].upper()}")
                        st.json(app['details'])
                        st.write(f"*Created at: {app['created_at']}*")
                        notes = st.text_input("Reviewer Notes", key=f"notes_{app['id']}")
                        
                    with cols[1]:
                        if st.button("Approve", type="primary", key=f"btn_app_{app['id']}"):
                            requests.post(f"{API_BASE_URL}/approvals/{app['id']}/approve", json={"notes": notes})
                            st.success("Approved!")
                            st.rerun()
                    with cols[2]:
                        if st.button("Reject", key=f"btn_rej_{app['id']}"):
                            requests.post(f"{API_BASE_URL}/approvals/{app['id']}/reject", json={"notes": notes})
                            st.error("Rejected.")
                            st.rerun()
                            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching dashboard data: {e}")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat Interface", "Approval Dashboard"])

if page == "Chat Interface":
    chat_interface()
else:
    dashboard_interface()

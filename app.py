import streamlit as st
import requests
import os
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Microbiology Farm Assistant",
    page_icon="🔬",
    layout="wide",
)

# --- Sidebar ---
with st.sidebar:
    st.title("🔬 Microbiology Farm")
    st.markdown("### Choose Your Persona")
    persona = st.radio(
        "Select your role:",
        ("Scientist", "Mission Architect"),
        label_visibility="collapsed"
    )

    if persona == "Scientist":
        st.info("""
        **Your goal:** Generate new hypotheses.
        - Ask about connections between studies.
        - Explore experimental methods.
        - Look for gaps in the current research.
        """)
    else:  # Mission Architect
        st.info("""
        **Your goal:** Explore the Moon and Mars safely and efficiently.
        - Ask about material durability under stress.
        - Inquire about structural integrity.
        - Look for findings related to long-duration missions.
        """)

# --- Main Chat Interface ---
st.title("Microbiology Farm Assistant")
st.markdown("Explore a knowledge base of microbiology articles through conversation.")

# Get the backend API URL from an environment variable, with a local fallback
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/ask")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you explore the microbiology knowledge base today?"}]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display context if it exists in the message
        if "context" in message and message["context"]:
            with st.expander("View Context Used"):
                st.markdown(message["context"])

# Accept user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call the FastAPI backend
                response = requests.post(API_URL, json={"question": prompt})
                response.raise_for_status()
                
                data = response.json()
                answer = data.get("answer", "Sorry, I couldn't find an answer.")
                context = data.get("context", "")

                st.markdown(answer)
                
                if context:
                    with st.expander("View Context Used"):
                        st.markdown(context)
                
                # Add assistant response to chat history
                assistant_message = {"role": "assistant", "content": answer, "context": context}
                st.session_state.messages.append(assistant_message)

            except requests.exceptions.RequestException as e:
                error_message = f"Error connecting to the backend API: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

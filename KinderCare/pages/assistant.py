import streamlit as st
from ai_assistant import chat_with_history, get_quick_responses

def render():
    st.markdown("""
        <style>
            .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2,
            .stMarkdown h3, label, .stText, p, h1, h2, h3, span,
            .stChatMessage p, .stChatMessage span, .stChatMessage div,
            [data-testid="stChatMessageContent"] p,
            [data-testid="stChatMessageContent"] span,
            [data-testid="stChatMessageContent"] {
                color: #1E90FF !important;
            }
            .stChatMessage {
                background-color: rgba(30, 144, 255, 0.08) !important;
                border-radius: 10px;
            }
            [data-testid="stChatMessage-user"] {
                background-color: #FFFFFF !important;
                border-radius: 10px;
            }
            .stButton > button {
                background-color: #1E90FF !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
            }
            .stButton > button:hover {
                background-color: #1565C0 !important;
            }
            .stChatInputContainer {
                border: 2px solid #1E90FF !important;
                border-radius: 10px !important;
            }
            hr {
                border-color: #1E90FF !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#1E90FF;'>🤖 KinderCare AI Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1E90FF;'>Ask me anything about your child's health, vaccinations, or wellness.</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown("<p style='color:#1E90FF; font-weight:bold;'>💡 Quick Questions:</p>", unsafe_allow_html=True)

    quick = get_quick_responses()
    col1, col2 = st.columns(2)
    for i, question in enumerate(quick):
        col = col1 if i % 2 == 0 else col2
        if col.button(question, key=f"quick_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("KinderCare AI is thinking..."):
                reply = chat_with_history(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask KinderCare AI anything about your child's health...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_history(st.session_state.chat_history)
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

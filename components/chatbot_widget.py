import datetime
import streamlit as st
from utils.chatbot import query_groq_chatbot

def render_chatbot_widget(persona: str = "Wheelchair User"):
    """
    Renders an interactive floating AccessIQ AI Assistant chatbot widget in the bottom-right corner.
    Features:
    - Floating circular FAB button with purple gradient glow and notification badge
    - Toggle window with Chat History, Clear Chat, New Chat
    - Real-time Groq API integration (Llama-3.3-70b) with Gemini fallback
    - Markdown rendering, timestamps, typing indicator, and responsive container
    """
    # Initialize session state for chatbot
    if "chatbot_open" not in st.session_state:
        st.session_state["chatbot_open"] = False
    if "chatbot_messages" not in st.session_state:
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["chatbot_messages"] = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm **AccessIQ AI Assistant**. Ask me anything about urban accessibility standards, RPWD/ADA guidelines, platform predictions, or smart city recommendations!",
                "time": now_str
            }
        ]
    if "chatbot_unread" not in st.session_state:
        st.session_state["chatbot_unread"] = True

    # FAB Toggle Button HTML
    is_open = st.session_state["chatbot_open"]
    has_unread = st.session_state.get("chatbot_unread", False) and not is_open

    # Streamlit button container for FAB
    fab_col1, fab_col2 = st.columns([1, 1])
    
    # We render the floating button controls using st.components or styled expander / container
    # Floating FAB & Window via Streamlit sidebar / container block
    with st.sidebar:
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">🤖 AccessIQ AI Floating Assistant</div>', unsafe_allow_html=True)
        
        bot_btn_label = "❌ Close Assistant" if is_open else "💬 Open AI Chatbot"
        if st.button(bot_btn_label, key="toggle_chatbot_fab_sidebar", use_container_width=True):
            st.session_state["chatbot_open"] = not is_open
            st.session_state["chatbot_unread"] = False
            st.rerun()

    # RENDER CHATBOT FLOATING WINDOW WHEN OPEN
    if is_open:
        with st.container():
            st.markdown("""
            <div style="background: var(--card-bg-solid); border: 1px solid var(--card-border); border-radius: var(--radius-2xl); padding: 1.2rem; margin-top: 1rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-xl); animation: slideUp 0.35s ease;">
                <div style="display: flex; justify-content: space-between; align-items: center; background: var(--gradient-primary); padding: 0.8rem 1.2rem; border-radius: var(--radius-lg); color: white; margin-bottom: 1rem;">
                    <div>
                        <div style="font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1rem;">🤖 AccessIQ AI Assistant</div>
                        <div style="font-size: 0.72rem; opacity: 0.9;">Powered by Groq LLaMA-3 & Gemini AI</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Actions Bar (Clear Chat, New Chat)
            ac1, ac2, ac3 = st.columns([1, 1, 1])
            with ac1:
                if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
                    now_str = datetime.datetime.now().strftime("%I:%M %p")
                    st.session_state["chatbot_messages"] = [{
                        "role": "assistant",
                        "content": "Chat history cleared. How can I help you now?",
                        "time": now_str
                    }]
                    st.rerun()
            with ac2:
                if st.button("✨ New Topic", key="new_chat_btn", use_container_width=True):
                    now_str = datetime.datetime.now().strftime("%I:%M %p")
                    st.session_state["chatbot_messages"] = [{
                        "role": "assistant",
                        "content": "Started a new conversation session. Ask any accessibility question!",
                        "time": now_str
                    }]
                    st.rerun()
            with ac3:
                if st.button("❌ Close Window", key="close_chat_btn", use_container_width=True):
                    st.session_state["chatbot_open"] = False
                    st.rerun()

            st.markdown("<hr style='border-color: var(--card-border-subtle); margin: 0.8rem 0;'>", unsafe_allow_html=True)

            # Chat History Container
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state["chatbot_messages"]:
                    role = msg.get("role", "assistant")
                    content = msg.get("content", "")
                    msg_time = msg.get("time", "")

                    if role == "user":
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin-bottom: 0.6rem;">
                            <div class="chat-bubble chat-bubble-user">
                                <div>{content}</div>
                                <div class="chat-timestamp" style="text-align: right; color: rgba(255,255,255,0.7);">{msg_time}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 0.6rem;">
                            <div class="chat-bubble chat-bubble-assistant">
                                <div>{content}</div>
                                <div class="chat-timestamp" style="color: var(--text-dim);">{msg_time}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Chat Input Form
            with st.form("floating_chat_form", clear_on_submit=True):
                user_msg = st.text_input("Ask AccessIQ AI...", placeholder="Type your accessibility or project question here...", key="chat_input_val")
                send_chat = st.form_submit_button("🚀 Send Message")

            if send_chat and user_msg.strip():
                now_time = datetime.datetime.now().strftime("%I:%M %p")
                st.session_state["chatbot_messages"].append({
                    "role": "user",
                    "content": user_msg.strip(),
                    "time": now_time
                })
                
                # Fetch AI response
                with st.spinner("🤖 AccessIQ AI is generating response..."):
                    bot_response = query_groq_chatbot(
                        st.session_state["chatbot_messages"],
                        persona=persona
                    )
                
                resp_time = datetime.datetime.now().strftime("%I:%M %p")
                st.session_state["chatbot_messages"].append({
                    "role": "assistant",
                    "content": bot_response,
                    "time": resp_time
                })
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import requests

st.set_page_config(page_title="Hiring Assistant Chatbot", page_icon="💬")
st.title("🤖 Hiring Assistant Chatbot")


info_questions = [
    "What's your full name?",
    "What's your email address?",
    "What's your mobile number?",
    "How many years of experience do you have?",
    "What position are you applying for?",
    "List your tech stack (languages, frameworks, tools, etc.)"
]

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = -1  
if "answers" not in st.session_state:
    st.session_state.answers = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []

if "interview_step" not in st.session_state:
    st.session_state.interview_step = 0

# Show chat history
for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# Step -1: Initial greeting
if st.session_state.step == -1:
    welcome = "👋 Hi there! I'm your Hiring Assistant. I'll ask you some quick questions to get started."
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    st.session_state.step += 1
    st.rerun()

# Step 0 → N: Ask personal info
elif st.session_state.step < len(info_questions):
    current_question = info_questions[st.session_state.step]

    # Show question once
    if not any(q["content"] == current_question for q in st.session_state.chat_history if q["role"] == "assistant"):
        st.session_state.chat_history.append({"role": "assistant", "content": current_question})
        st.rerun()

    user_input = st.chat_input("Your answer...")

    if user_input is not None:
        user_input = user_input.strip()

        # Check if input is empty
        if user_input == "":
            st.warning(" Please provide an answer to proceed.")
        elif current_question == "What's your mobile number?" and not user_input.isdigit():
            st.warning("Please enter a valid mobile number (digits only).")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.answers.append(user_input)
            st.session_state.step += 1
            st.rerun()

# Step N+1: Generate interview questions from FastAPI
elif st.session_state.interview_questions == []:
    name, email, number, experience, position, tech_stack = st.session_state.answers
    payload = {
        "name": name,
        "email": email,
        "number": int(number),
        "experience": experience,
        "position": position,
        "tech_stack": tech_stack
    }

    with st.chat_message("assistant"):
        st.markdown("Great! Now generating your interview questions...")

    try:
        res = requests.post("https://hirring-assistant.onrender.com/generate-questions", json=payload)
        res.raise_for_status()
        q_text = res.json()["questions"]

        # Clean and store questions
        questions = [q.strip() for q in q_text.split('\n') if q.strip()]
        st.session_state.interview_questions = questions
        st.rerun()

    except Exception as e:
        st.error(f" Error: {e}")

# Interview questions one by one
elif st.session_state.interview_step < len(st.session_state.interview_questions):
    current_question = st.session_state.interview_questions[st.session_state.interview_step]

    if not any(q["content"] == current_question for q in st.session_state.chat_history if q["role"] == "assistant"):
        st.session_state.chat_history.append({"role": "assistant", "content": current_question})
        st.rerun()

    user_input = st.chat_input("Your answer...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.interview_step += 1
        st.rerun()

# Final summary and thank you
else:
    summary = " **Here's a summary of your submitted information:**\n\n"
    for i, answer in enumerate(st.session_state.answers):
        summary += f"- **{info_questions[i]}**: {answer}\n"

    st.session_state.chat_history.append({"role": "assistant", "content": summary})
    st.session_state.step += 1  # Just to avoid repeating

    with st.chat_message("assistant"):
        st.markdown(summary)
        st.markdown("Thank you for completing the interview! We’ll review your responses and get back to you soon. Good luck! ")

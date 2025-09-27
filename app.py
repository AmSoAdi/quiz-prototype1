import streamlit as st
from transformers import pipeline

# ------------------------------
# Load Hugging Face QG model
# ------------------------------
@st.cache_resource
def load_qg_model():
    return pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")

qg_model = load_qg_model()

def generate_questions(text, num=2):
    results = qg_model(text, max_length=64, num_return_sequences=num, do_sample=True)
    return [r['generated_text'] for r in results]


# ------------------------------
# Session setup
# ------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "mode" not in st.session_state:
    st.session_state.mode = None


st.set_page_config(page_title="AI Quiz Platform", layout="centered")


# ------------------------------
# Pages
# ------------------------------

def home():
    st.title("AI-Powered Quiz Platform 🎓")
    st.subheader("Personalized • Adaptive • Smart Learning")

    st.markdown("""
    Welcome to our prototype demo!  

    Choose a mode to continue:  
    - 📝 **Test Mode** → Quick practice & small class tests  
    - 📘 **Learner Mode** → Concept-building with hints & explanations  
    - ⏳ **Exam Mode** → Real exam simulation with leaderboard  
    """)

    if st.button("Test Mode"):
        st.session_state.mode = "test"
        st.session_state.page = "input"
    if st.button("Learner Mode"):
        st.session_state.mode = "learner"
        st.session_state.page = "input"
    if st.button("Exam Mode"):
        st.session_state.mode = "exam"
        st.session_state.page = "input"

    if st.button("Future Scope"):
        st.session_state.page = "future"


def input_page():
    st.header(f"Teacher Input ({st.session_state.mode.capitalize()} Mode)")
    
    topic = st.text_input("Enter Topic (e.g., Physics Motion)", 
                          value=st.session_state.get("topic", ""))
    num_qs = st.slider("Number of Questions", 1, 5, 
                       value=st.session_state.get("num_qs", 3))

    st.session_state.topic = topic
    st.session_state.num_qs = num_qs

    if st.button("Generate Quiz"):
        # Generate questions once and store in session_state
        st.session_state.ai_questions = generate_questions(f"Explain the basics of {topic}", num=num_qs)
        st.session_state.page = "quiz"


# ------------------------------
# Quiz Page
# ------------------------------
def quiz_page():
    st.header(f"Student Quiz Attempt – {st.session_state.mode.capitalize()} Mode")
    topic = st.session_state.get("topic", "General Knowledge")
    st.write(f"Topic: **{topic}**")

    # Retrieve AI-generated questions from session_state
    ai_questions = st.session_state.get("ai_questions", [])

    if not ai_questions:
        st.warning("No questions generated yet. Go back and generate a quiz.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
        return

    # ------------------------------
    # Display AI-generated questions
    # ------------------------------
    st.subheader("AI-Generated Questions")
    for i, q in enumerate(ai_questions):
        answer_key = f"ai_answer_{i}"
        st.text_area(
            f"Q{i+1}: {q}",
            value=st.session_state.get(answer_key, ""),
            key=answer_key
        )
        if st.session_state.mode == "learner":
            st.caption("Hint: Think about the basic principles of this topic.")

    # ------------------------------
    # Sample MCQ
    # ------------------------------
    sample_mcq = {
        "question": "What is the SI unit of force?",
        "options": ["Newton", "Joule", "Watt", "Pascal"],
        "answer": "Newton",
        "explanation": "Force is measured in Newtons, named after Isaac Newton."
    }

    mcq_key = "mcq1_answer"
    # Use 'value' instead of 'index' to avoid int/string errors
    current_value = st.session_state.get(mcq_key, sample_mcq["options"][0])
    st.radio(
        sample_mcq["question"],
        sample_mcq["options"],
        index=None,        # Remove index, use value instead
        key=mcq_key        # Stores the selected string in session_state
    )
    if st.session_state.mode == "learner":
        st.caption(f"Hint: The answer is named after a famous scientist.")

    # ------------------------------
    # Submit button
    # ------------------------------
    if st.button("Submit Quiz"):
        st.session_state.page = "result"


# ------------------------------
# Result Page
# ------------------------------
def result_page():
    st.header(f"Results & Leaderboard – {st.session_state.mode.capitalize()} Mode")
    topic = st.session_state.get("topic", "General Knowledge")
    ai_questions = st.session_state.get("ai_questions", [])

    # ------------------------------
    # Demo scoring
    # ------------------------------
    score = 0
    for i in range(len(ai_questions)):
        ans = st.session_state.get(f"ai_answer_{i}", "")
        if ans.strip():  # count non-empty answers
            score += 1

    # MCQ scoring
    sample_mcq = {
        "question": "What is the SI unit of force?",
        "options": ["Newton", "Joule", "Watt", "Pascal"],
        "answer": "Newton",
        "explanation": "Force is measured in Newtons, named after Isaac Newton."
    }
    user_mcq_answer = st.session_state.get("mcq1_answer", sample_mcq["options"][0])
    if user_mcq_answer == sample_mcq["answer"]:
        score += 1

    if st.session_state.mode == "learner":
        st.success("✅ In Learner Mode, scores matter less — focus on the explanations.")
    else:
        st.success(f"Your Score: {score}/{len(ai_questions)+1}")

    # ------------------------------
    # Display explanations
    # ------------------------------
    st.subheader("Explanations:")
    for i, q in enumerate(ai_questions):
        user_ans = st.session_state.get(f"ai_answer_{i}", "")
        st.write(f"• Q{i+1}: {q}")
        st.write(f"  - Your Answer: {user_ans}")
        st.write(f"  - Explanation: Based on generated content and key concepts.")

    # MCQ explanation
    st.write(f"• MCQ: {sample_mcq['question']}")
    st.write(f"  - Your Answer: {user_mcq_answer}")
    st.write(f"  - Correct Answer: {sample_mcq['answer']}")
    st.write(f"  - Explanation: {sample_mcq['explanation']}")

    # Leaderboard for exam mode
    if st.session_state.mode == "exam":
        st.subheader("Leaderboard (Demo)")
        st.write("1. Student A – 3/3")  
        st.write("2. You – 2/3")  
        st.write("3. Student B – 1/3")  

    if st.button("Back to Home"):
        st.session_state.page = "home"



def future_page():
    st.header("Future Scope 🚀")
    st.markdown("""
    **1. PDF-to-Quiz with RAG** → Upload past papers & auto-generate quizzes  
    **2. Advanced Descriptive Evaluation** → AI-based semantic grading  
    **3. Real-Time Analytics Dashboard** → Teacher insights & progress tracking  
    **4. Multi-Platform Expansion** → Mobile app + LMS integration  
    **5. Scalability & Security** → Cloud infra + anti-cheating tools  
    """)
    if st.button("Back to Home"):
        st.session_state.page = "home"


# ------------------------------
# Router
# ------------------------------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "input":
    input_page()
elif st.session_state.page == "quiz":
    quiz_page()
elif st.session_state.page == "result":
    result_page()
elif st.session_state.page == "future":
    future_page()

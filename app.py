import streamlit as st
from audio_recorder_streamlit import audio_recorder
from datetime import date

from utils.ai_client import (
    summarize_and_quiz,
    evaluate_spoken_answer,
    transcribe_audio,
    generate_study_plan,
)
from utils.spaced_repetition import next_review, is_due, DIFFICULTY_LABELS
from utils.pomodoro import run_countdown

st.set_page_config(
    page_title="EduPulse AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem;}
    .stButton>button {border-radius: 10px; font-weight: 600;}
    .quiz-card {padding: 1rem 1.2rem; border-radius: 12px;
                background: rgba(120,120,255,0.06); margin-bottom: 1rem;}
    .flashcard {padding: 2.5rem; border-radius: 16px; text-align: center;
                background: linear-gradient(135deg,#6366f1,#8b5cf6);
                color: white; font-size: 1.4rem; min-height: 180px;
                display: flex; align-items: center; justify-content: center;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "cards" not in st.session_state:
    st.session_state.cards = []
if "current_card" not in st.session_state:
    st.session_state.current_card = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🚀 EduPulse AI")
    st.caption("Բոլորը մեկում ուսումնական հարթակ")
    page = st.radio(
        "Ընտրիր բաժինը",
        [
            "🗂️ Կոնսպեկտ և Քվիզ",
            "🎙️ Ձայնային Օգնական",
            "🃏 Ֆլեշ-քարտեր",
            "⏱️ Քննական Քարտեզ",
        ],
        label_visibility="collapsed",
    )

# ---------- Page 1: Summarizer & Quiz ----------
if page == "🗂️ Կոնսպեկտ և Քվիզ":
    st.header("🗂️ Խելացի Կոնսպեկտավորող և Քվիզ Գեներատոր")
    text = st.text_area("Տեղադրիր դասի նյութը", height=260,
                        placeholder="Կպցրու դասագրքի տեքստը այստեղ...")
    num_q = st.slider("Հարցերի քանակ", 3, 10, 5)

    if st.button("✨ Կազմել սեղմագիր և թեստ", type="primary"):
        if not text.strip():
            st.warning("Խնդրում ենք նախ տեղադրել տեքստ։")
        else:
            with st.spinner("AI-ը վերլուծում է նյութը..."):
                try:
                    st.session_state.quiz = summarize_and_quiz(text, num_q)
                    st.session_state.user_answers = {}
                except Exception as e:
                    st.error(f"Սխալ՝ {e}")

    quiz = st.session_state.quiz
    if quiz:
        tab1, tab2 = st.tabs(["📝 Սեղմագիր", "❓ Թեստ"])
        with tab1:
            st.markdown(quiz.get("summary", ""))
        with tab2:
            for i, q in enumerate(quiz.get("questions", [])):
                st.markdown(f'<div class="quiz-card"><b>{i+1}. {q["question"]}</b></div>',
                            unsafe_allow_html=True)
                choice = st.radio(
                    "Ընտրիր պատասխանը",
                    q["options"],
                    key=f"q_{i}",
                    index=None,
                    label_visibility="collapsed",
                )
                if st.button("Ստուգել", key=f"check_{i}"):
                    st.session_state.user_answers[i] = choice
                if i in st.session_state.user_answers:
                    chosen = st.session_state.user_answers[i]
                    if chosen == q["options"][q["answer_index"]]:
                        st.success("✅ Ճիշտ է։")
                    else:
                        st.error(f"❌ Սխալ։ Ճիշտ պատասխանն է՝ {q['options'][q['answer_index']]}")
                    st.info(q.get("explanation", ""))
                  # ---------- Page 2: Voice Study Buddy ----------
elif page == "🎙️ Ձայնային Օգնական":
    st.header("🎙️ Ձայնային Օգնական")
    topic = st.text_input("Թեմա", placeholder="Օրինակ՝ Հայաստանի Առաջին Հանրապետություն")
    st.write("Սեղմիր կոճակը, պատմիր թեման և նորից սեղմիր՝ դադարեցնելու համար։")
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#6366f1",
        icon_size="3x",
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        if st.button("📊 Վերլուծել պատասխանը", type="primary"):
            if not topic.strip():
                st.warning("Նշիր թեման։")
            else:
                with st.spinner("Whisper-ը լսում է, AI-ը վերլուծում..."):
                    try:
                        transcript = transcribe_audio(audio_bytes)
                        st.markdown("Դու ասացիր՝")
                        st.write(transcript)
                        feedback = evaluate_spoken_answer(topic, transcript)
                        st.markdown("### Հետադարձ կապ")
                        st.markdown(feedback)
                    except Exception as e:
                        st.error(f"Սխալ՝ {e}")

# ---------- Page 3: Flashcards ----------
elif page == "🃏 Ֆլեշ-քարտեր":
    st.header("🃏 Ադապտիվ Ֆլեշ-քարտեր")

    with st.expander("➕ Ավելացնել նոր քարտ", expanded=not st.session_state.cards):
        with st.form("add_card", clear_on_submit=True):
            front = st.text_input("Առջևի մասը (հարց)")
            back = st.text_area("Հետևի մասը (պատասխան)")
            if st.form_submit_button("Ավելացնել"):
                if front.strip() and back.strip():
                    st.session_state.cards.append({
                        "front": front.strip(),
                        "back": back.strip(),
                        "due_at": None,
                        "interval_minutes": 0,
                        "ease": 2.5,
                        "last_rating": None,
                    })
                    st.success("Քարտը ավելացվեց։")
                else:
                    st.warning("Լրացրու երկու դաշտերը։")

    due_cards = [c for c in st.session_state.cards if is_due(c)]

    if not st.session_state.cards:
        st.info("Դեռ քարտեր չկան։ Ավելացրու առաջինը վերևում։")
    elif not due_cards:
        st.success("🎉 Այս պահին կրկնելու քարտ չկա։ Վերադարձիր մի փոքր ավելի ուշ։")
    else:
        if st.session_state.current_card not in due_cards:
            st.session_state.current_card = due_cards[0]
            st.session_state.show_answer = False

        card = st.session_state.current_card
        st.caption(f"Մնացել է՝ {len(due_cards)} քարտ")
        st.markdown(f'<div class="flashcard">{card["front"]}</div>', unsafe_allow_html=True)

        if not st.session_state.show_answer:
            if st.button("👁️ Ցույց տալ պատասխանը", type="primary", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        else:
            st.markdown(f"Պատասխան՝ {card['back']}")
            c1, c2, c3 = st.columns(3)
            for col, rating in zip((c1, c2, c3), ("hard", "medium", "easy")):
                if col.button(DIFFICULTY_LABELS[rating], use_container_width=True, key=f"r_{rating}"):
                    next_review(card, rating)
                    st.session_state.current_card = None
                    st.session_state.show_answer = False
                    st.rerun()

# ---------- Page 4: Roadmap & Pomodoro ----------
elif page == "⏱️ Քննական Քարտեզ":
    st.header("⏱️ Քննական Ճանապարհային Քարտեզ և Pomodoro")

    left, right = st.columns([3, 2])

    with left:
        st.subheader("📅 AI Roadmap")
        subject = st.text_input("Առարկա", placeholder="Օր.՝ Կենսաբանություն")
        exam_date = st.date_input("Քննության օրը", min_value=date.today())
        topics = st.text_area("Թեմաներ (ստորակետով)", placeholder="Բջիջ, ֆոտոսինթեզ, գենետիկա")
        if st.button("🗺️ Կազմել պլանը", type="primary"):
            days_left = (exam_date - date.today()).days
            if not subject.strip() or not topics.strip():
                st.warning("Լրացրու առարկան և թեմաները։")
            elif days_left < 0:
                st.warning("Քննության օրը արդեն անցել է։")
            else:
                with st.spinner("Կազմվում է պլանը..."):
                    try:
                        st.session_state.roadmap = generate_study_plan(
                            subject, exam_date.isoformat(), days_left, topics
                        )
                    except Exception as e:
                        st.error(f"Սխալ՝ {e}")
        if st.session_state.roadmap:
            st.markdown(st.session_state.roadmap)
    with right:
        st.subheader("🍅 Focus Timer")
        work_min = st.number_input("Աշխատանք (րոպե)", 1, 60, 25)
        break_min = st.number_input("Ընդմիջում (րոպե)", 1, 30, 5)
        placeholder = st.empty()
        placeholder.metric("Մնացել է", f"{work_min:02d}:00")
        if st.button("▶️ Սկսել Pomodoro", use_container_width=True):
            st.toast("Աշխատանքի ժամանակ սկսվեց 🎯")
            run_countdown(int(work_min * 60), placeholder)
            st.toast("Ժամանակը լրացավ։ Ընդմիջո՛ւմ ☕")
            run_countdown(int(break_min * 60), placeholder)
            st.success("Pomodoro-ի ցիկլը ավարտվեց։ Հանգստացիր և շարունակիր։")

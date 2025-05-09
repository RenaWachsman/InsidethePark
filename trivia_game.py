import streamlit as st
from trivia import get_random_trivia_question


class TriviaGame:
    def __init__(self, team_id):
        self.team_id = team_id
        st.session_state.setdefault("pitches", 0)
        st.session_state.setdefault("strikes", 0)
        st.session_state.setdefault("bases", 0)
        st.session_state.setdefault("status", "At bat...")
        self.question_key = f"trivia_question_{team_id}"
        self.submit_key = f"submitted_{team_id}"
        self.process_key = f"processed_{team_id}"

        if self.question_key not in st.session_state:
            self.new_question()

    def new_question(self):
        q = get_random_trivia_question(int(self.team_id))
        self.current_question = q
        st.session_state[self.question_key] = q
        st.session_state["pitches"] = st.session_state.get("pitches", 0) + 1
        st.session_state[self.submit_key] = False
        st.session_state[self.process_key] = False

    def get_question(self):
        return st.session_state.get(self.question_key)

    def submit_answer(self, answer):
        question = self.get_question()
        if question.is_correct(answer):
            st.session_state["bases"] = st.session_state.get("bases", 0) + 1
            st.success("✅ Correct! That's some contact!")
        else:
            st.session_state["strikes"] = (
                st.session_state.get("strikes", 0) + 1
            )
            st.error(f"❌ Strike! The correct answer was: \
                     {question.correct_answer}")
        st.session_state[self.process_key] = True

    def next_pitch(self):
        for key in [self.question_key, self.submit_key, self.process_key]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    def is_game_over(self):
        return (
            st.session_state.get("strikes", 0) >= 3
            or st.session_state.get("pitches", 0) >= 5
        )

    def finalize_status(self):
        if st.session_state.get("strikes", 0) == 3:
            st.session_state["status"] = "Three Strikes - You're OUT!"
        else:
            bases = st.session_state.get("bases", 0)
            outcomes = {
                1: "Single! You got 1 correct!",
                2: "Double! You got 2 correct!",
                3: "Triple! You got 3 correct!",
                4: "Home Run! You got 4 correct!",
                5: "Grand Slam! All 5 correct!",
            }
            st.session_state["status"] = outcomes.get(bases, "Game Over!")


def new_game():
    for key in ["pitches", "strikes", "bases", "status"]:
        st.session_state.pop(key, None)

    team_id = st.session_state.get("selected_team")
    if team_id:
        for suffix in ["trivia_question", "submitted", "processed"]:
            st.session_state.pop(f"{suffix}_{team_id}", None)

# This module contains a class and function for the Trivia Game
import streamlit as st
from trivia_question import get_random_trivia_question
from database import get_team_by_id


class TriviaGame:
    # Set up the details of a game
    def __init__(self, team_id):
        self.team_id = team_id
        st.session_state.setdefault("pitches", 0)
        st.session_state.setdefault("strikes", 0)
        st.session_state.setdefault("bases", 0)
        st.session_state.setdefault("status", "At bat...")
        self.question_key = f"trivia_question_{team_id}"
        self.submit_key = f"submitted_{team_id}"
        self.process_key = f"processed_{team_id}"
        # start every game with a question
        if self.question_key not in st.session_state:
            self.new_question()

    # Function gets a question

    def new_question(self):
        q = get_random_trivia_question(int(self.team_id))
        self.current_question = q
        st.session_state[self.question_key] = q
        # increment the "pitches" (questions) count
        st.session_state["pitches"] = st.session_state.get("pitches", 0) + 1
        # reset the keys to track submit and new question
        st.session_state[self.submit_key] = False
        st.session_state[self.process_key] = False

    # Returns the current question

    def get_question(self):
        return st.session_state.get(self.question_key)

    # Manages a user submitting an answer
    def submit_answer(self, answer):
        question = self.get_question()
        # When it's correct increment correct/bases
        if question.is_correct(answer):
            st.session_state["bases"] = st.session_state.get("bases", 0) + 1
            st.success("✅ Correct! That's some contact!")
        else:
            # When it's incorrect increment incorrect/strikes
            st.session_state["strikes"] = (
                st.session_state.get("strikes", 0) + 1
            )
            st.error("❌ Strike! The correct answer was:"
                     + f"{question.correct_answer}"
                     )
        # Tracks that submit was clicked
        st.session_state[self.process_key] = True

    def next_pitch(self):
        # Reset some of session state for new pitch
        for key in [self.question_key, self.submit_key, self.process_key]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    def is_game_over(self):
        # Checks if game is ended by pitches and strikes
        return (
            st.session_state.get("strikes", 0) >= 3
            or st.session_state.get("pitches", 0) >= 5
        )

    def finalize_status(self):
        # Sets ending message for when the game ends and stores it
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
    # Starts a new game by resetting information and getting team again
    for key in ["pitches", "strikes", "bases", "status"]:
        st.session_state.pop(key, None)

    team_id = st.session_state.get("selected_team")
    if team_id:
        for suffix in ["trivia_question", "submitted", "processed"]:
            st.session_state.pop(f"{suffix}_{team_id}", None)


# Function to play the game


def st_game_play():
    with st.expander("📖 The Playbook"):
        st.markdown("""
            1. **Team Selection**: Pick your favorite baseball team.
            2. **Answer Questions**: You'll be asked 5 trivia questions based
            on your selected team and its players.
            3. **Scoring**:
                - Correct answer = **Base**
                - Wrong answer = **Strike**
            4. **Game Rules**:
                - **3 strikes** and you're out.
                - You get **5 pitches** (questions) max.
                - Game ends after 5 questions or 3 strikes.
            5. **Performance Grades**:
                - **1 Correct**: "Single!"
                - **2 Correct**: "Double!"
                - **3 Correct**: "Triple!"
                - **4 Correct**: "Home Run!"
                - **5 Correct**: "Grand Slam!"
            """)

    # Game State Initialization
    for key, value in [('pitches', 0), ('strikes', 0), ('bases', 0),
                       ('status', "At bat...")]:
        if key not in st.session_state:
            st.session_state[key] = value

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("## Play Ball!")
        team = get_team_by_id(int(st.session_state['selected_team']))
        st.markdown(f"##### Your team: {team['name']}")
        team_id = st.session_state['selected_team']
        question_key = f"trivia_question_{team_id}"
        submit_key = f"submitted_{team_id}"
        process_key = f"processed_{team_id}"

        # Load new question if not already present
        if question_key not in st.session_state:
            st.session_state[question_key] = get_random_trivia_question(
                int(team_id))
            st.session_state.pitches += 1

        q = st.session_state[question_key]

        if q:
            if q.image_url:
                st.image(q.image_url, width=150)

            user_answer = st.radio(q.question, q.choices,
                                   key=f"answer_{question_key}")

            if submit_key not in st.session_state:
                st.session_state[submit_key] = False
            if process_key not in st.session_state:
                st.session_state[process_key] = False

            if st.button("Submit"):
                st.session_state[submit_key] = True

            if st.session_state[submit_key] \
                    and not st.session_state[process_key]:
                if q.is_correct(user_answer):
                    st.success("✅ Correct! That's some contact!")
                    st.session_state.bases += 1
                else:
                    st.error(
                        "❌ Strike! The correct answer was: "
                        + f"{q.correct_answer}"
                    )
                    st.session_state.strikes += 1
                st.session_state[process_key] = True

            if st.session_state[submit_key]:
                if (st.session_state.pitches < 5 and
                        st.session_state.strikes < 3):
                    if st.button("Next Pitch"):
                        del st.session_state[question_key]
                        del st.session_state[submit_key]
                        del st.session_state[process_key]
                        st.rerun()
                else:
                    if st.session_state.strikes == 3:
                        st.session_state.status = "Three Strikes - You're OUT!"
                    else:
                        outcomes = {
                            1: "Single! You got 1 correct!",
                            2: "Double! You got 2 correct!",
                            3: "Triple! You got 3 correct!",
                            4: "Home Run! You got 4 correct!",
                            5: "Grand Slam! All 5 correct!",
                        }
                        st.session_state.status = outcomes.get(
                            st.session_state.bases, "Game Over!")
                    st.markdown(
                        f"#### GAME OVER! {st.session_state.status}")
    # Display Scoreboard
    with col2:
        st.markdown("## Scoreboard ")
        st.markdown("####")
        st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 1rem;
                border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                <p style='font-size: 18px;'>⚾ <strong>Pitches:</strong>
                    {st.session_state.pitches}</p>
                <p style='font-size: 18px;'>🧮 <strong>Pitches Remaining: \
                    </strong>
                    {5 - st.session_state.pitches}</p>
                <p style='font-size: 18px;'>❌ <strong>Strikes:</strong>
                    {st.session_state.strikes}</p>
                <p style='font-size: 18px;'>✅ <strong>Correct:</strong>
                    {st.session_state.bases}</p>
                <p style='font-size: 18px;'>🏅 <strong>Status:</strong>
                    {st.session_state.status}</
            </div>
            """, unsafe_allow_html=True)

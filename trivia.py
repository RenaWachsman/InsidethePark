import random
import streamlit as st
from database import get_team_by_id, get_players_by_team_id, get_all_teams
from api import get_player_info, get_player_teams, get_player_honors


class TriviaQuestion:
    def __init__(self, question, correct_answer, choices, image_url=None):
        self.question = question
        self.correct_answer = correct_answer
        self.choices = choices
        self.image_url = image_url
        random.shuffle(self.choices)

    def is_correct(self, answer):
        return answer == self.correct_answer

    def to_dict(self):
        return {
            "question": self.question,
            "correct_answer": self.correct_answer,
            "choices": self.choices,
            "image_url": self.image_url
        }


def generate_basic_questions(player_row):
    name = player_row["name"]
    info = get_player_info(name)
    if not info:
        return []

    questions = []
    headshot_url = player_row["headshot_url"]

    # Q1: Nationality
    nationality = info.get("strNationality")
    if nationality and nationality not in ["USA", "United States", "Canada"]:
        distractors = ["USA", "Canada", "Mexico", "Japan"]
        wrong = [n for n in distractors if n != nationality]
        questions.append(TriviaQuestion(
            question=f"What is {name}'s nationality?",
            correct_answer=nationality,
            choices=random.sample(wrong, 3) + [nationality],
            image_url=headshot_url
        ))

    # Q2: Birthdate
    dob = info.get("dateBorn")
    if dob:
        fakes = [
            "1990-01-01", "1985-05-05", "1992-10-10", "1998-07-07"
        ]
        wrong = [d for d in fakes if d != dob]
        questions.append(TriviaQuestion(
            question=f"When was {name} born?",
            correct_answer=dob,
            choices=random.sample(wrong, 3) + [dob],
            image_url=headshot_url
        ))

    # Q3: Position
    position = info.get("strPosition")
    if position:
        wrong_positions = [
            "Catcher", "Pitcher", "First Base", "Outfielder", "Shortstop"
        ]
        wrong = [p for p in wrong_positions if p != position]
        questions.append(TriviaQuestion(
            question=f"What position does {name} play?",
            correct_answer=position,
            choices=random.sample(wrong, 3) + [position],
            image_url=headshot_url
        ))

    # Q4: Former Team
    teams = get_player_teams(info["idPlayer"])
    if teams:
        former = [t["former_team"] for t in teams if t.get("former_team")]
        if former:
            correct = former[0]
            all_teams = get_all_teams()
            wrong = all_teams[all_teams["name"] != correct]["name"] \
                .sample(3).tolist()
            questions.append(TriviaQuestion(
                question=f"Which team did {name} formerly play for?",
                correct_answer=correct,
                choices=wrong + [correct],
                image_url=headshot_url
            ))

    # Q5: Honors
    honors = get_player_honors(info["idPlayer"])
    if honors:
        honor_obj = honors[0]
        honor = honor_obj.get("honour")
        if honor:
            distractors = [
                "World Series MVP", "Cy Young", "Rookie of the Year",
                "Rawlings Gold Glove Award", "Silver Slugger Award"
            ]
            wrong = [h for h in distractors if h != honor]
            questions.append(TriviaQuestion(
                question=f"What honor has {name} received?",
                correct_answer=honor,
                choices=random.sample(wrong, 3) + [honor],
                image_url=headshot_url
            ))

    return questions


def generate_who_is_this_question(team_id):
    df = get_players_by_team_id(team_id)
    if df.shape[0] < 4:
        return None

    choices = df.sample(4)
    correct = choices.iloc[0]

    return TriviaQuestion(
        question="Who is this player?",
        correct_answer=correct["name"],
        choices=choices["name"].tolist(),
        image_url=correct["headshot_url"]
    )


def get_random_trivia_question(team_id):
    df = get_players_by_team_id(team_id)
    if df.empty:
        return None

    player = df.sample(1).iloc[0]

    question_types = [
        lambda: generate_who_is_this_question(team_id),
        lambda: random.choice(generate_basic_questions(player))
        if generate_basic_questions(player) else None,
    ]

    random.shuffle(question_types)
    for q_func in question_types:
        q = q_func()
        if q:
            return q

    return None


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
                        f"❌ Strike! The correct answer was: {q.correct_answer}")
                    st.session_state.strikes += 1
                st.session_state[process_key] = True

            if st.session_state[submit_key]:
                if st.session_state.pitches < 5 and st.session_state.strikes < 3:
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

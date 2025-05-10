# This module creates a trivia question class and function
import random
from database import get_players_by_team_id, get_all_teams
from api import get_player_info, get_player_teams, get_player_honors


class TriviaQuestion:
    def __init__(self, question, correct_answer, choices, image_url=None):
        self.question = question
        self.correct_answer = correct_answer
        self.choices = choices
        self.image_url = image_url
        random.shuffle(self.choices)

    # Returns if the answer submitted is correct
    def is_correct(self, answer):
        return answer == self.correct_answer
    # Assembles a dictionary for the Question

    def to_dict(self):
        return {
            "question": self.question,
            "correct_answer": self.correct_answer,
            "choices": self.choices,
            "image_url": self.image_url
        }

# Questions based of the player api's - include headshot


def generate_basic_questions(player_row):
    name = player_row["name"]
    # The first api
    info = get_player_info(name)
    if not info:
        return []

    questions = []
    headshot_url = player_row["headshot_url"]

    # Q1: Nationality
    nationality = info.get("strNationality")
    if nationality and nationality not in ["China", "United States", "Canada"]:
        distractors = ["United States", "Canada", "Mexico", "Japan"]
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

# Question who is this with the player image


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

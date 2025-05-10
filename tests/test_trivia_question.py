import pytest
import pandas as pd
from unittest.mock import patch
from trivia_question import (
    TriviaQuestion,
    generate_basic_questions,
    generate_who_is_this_question,
    get_random_trivia_question,
)


@pytest.fixture
def player_data():
    return {
        "name": "Mookie Betts",
        "headshot_url": "https://example.com/mookie_betts.jpg"
    }


@pytest.fixture
def team_players_data():
    return pd.DataFrame({
        "name": ["Player 1", "Player 2", "Player 3", "Player 4"],
        "headshot_url": [
            "https://example.com/player1.jpg",
            "https://example.com/player2.jpg",
            "https://example.com/player3.jpg",
            "https://example.com/player4.jpg"
        ]
    })


@pytest.fixture
def mock_functions(mocker):
    mocker.patch("api.get_player_info", return_value={
        "strNationality": "USA",
        "dateBorn": "1992-10-07",
        "strPosition": "Outfielder",
        "idPlayer": 123
    })
    mocker.patch("api.get_player_teams", return_value=[
                 {"former_team": "Red Sox"}])
    mocker.patch("api.get_player_honors", return_value=[{"honour": "MVP"}])
    mocker.patch("database.get_all_teams", return_value=pd.DataFrame({
        "name": ["Red Sox", "Dodgers", "Giants", "Yankees", "Mets"]
    }))


def test_trivia_question_init_sets_attributes():
    q = TriviaQuestion(
        question="What is the capital of Missouri?",
        correct_answer="Jefferson City",
        choices=["St. Louis", "Kansas", "Ferguson", "Jefferson City"],
        image_url="https://example.com/image.jpg"
    )
    assert q.question == "What is the capital of Missouri?"
    assert q.correct_answer == "Jefferson City"
    assert sorted(q.choices) == sorted(
        ["St. Louis", "Kansas", "Ferguson", "Jefferson City"]
    )
    assert q.image_url == "https://example.com/image.jpg"
    assert q.correct_answer in q.choices


def test_trivia_question_init_without_image_url():
    q = TriviaQuestion(
        question="2 + 2 = ?",
        correct_answer="4",
        choices=["3", "4", "5", "6"]
    )
    assert q.image_url is None
    assert sorted(q.choices) == sorted(["3", "4", "5", "6"])


@pytest.mark.parametrize("answer,expected", [
    ("Jefferson City", True),
    ("St. Louis", False),
    ("Kansas", False),
    ("Ferguson", False),
    ("Columbia", False),
])
def test_is_correct(answer, expected):
    q = TriviaQuestion(
        question="What is the capital of Missouri?",
        correct_answer="Jefferson City",
        choices=["St. Louis", "Kansas", "Ferguson", "Jefferson City"]
    )
    assert q.is_correct(answer) == expected


def test_to_dict():
    q = TriviaQuestion(
        question="What is the capital of Missouri?",
        correct_answer="Jefferson City",
        choices=["St. Louis", "Kansas", "Ferguson", "Jefferson City"],
        image_url="https://example.com/image.jpg"
    )
    result = q.to_dict()
    assert result["question"] == "What is the capital of Missouri?"
    assert result["correct_answer"] == "Jefferson City"
    assert sorted(result["choices"]) == sorted(
        ["St. Louis", "Kansas", "Ferguson", "Jefferson City"]
    )
    assert result["image_url"] == "https://example.com/image.jpg"


def assert_correct_answer_in_choices(question):
    assert question.correct_answer in question.choices, \
        "Correct answer should be in choices"


def test_generate_basic_questions_correct_answer_in_choices(player_data,
                                                            mock_functions):
    questions = generate_basic_questions(player_data)
    for q in questions:
        assert isinstance(q, TriviaQuestion)
        assert_correct_answer_in_choices(q)


@patch("trivia_question.get_players_by_team_id")
def test_generate_who_is_this_question_4_players(mock_get_players_by_team_id,
                                                 team_players_data):
    mock_get_players_by_team_id.return_value = team_players_data
    result = generate_who_is_this_question(1)
    assert isinstance(result, TriviaQuestion)
    assert result.question == "Who is this player?"
    assert len(result.choices) == 4
    assert result.correct_answer in result.choices


@patch("trivia_question.get_players_by_team_id")
@patch("random.choices")
def test_get_random_trivia_question(
    mock_random_choices, mock_get_players_by_team_id, team_players_data
):
    mock_get_players_by_team_id.return_value = team_players_data
    mock_random_choices.return_value = [generate_who_is_this_question]

    result = get_random_trivia_question(1)

    assert isinstance(result, TriviaQuestion)
    assert result.question
    assert isinstance(result.choices, list)
    assert result.correct_answer in result.choices

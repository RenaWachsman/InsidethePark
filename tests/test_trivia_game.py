import pytest
import streamlit as st
from unittest.mock import MagicMock
import trivia_question


# Fixtures

@pytest.fixture(autouse=True)
def reset_streamlit_session():
    """Clear Streamlit session before each test."""
    st.session_state.clear()


@pytest.fixture
def mock_get_random_trivia_question(monkeypatch):
    """Patch trivia.get_random_trivia_question before \
        TriviaGame is imported."""
    def _mock(team_id):
        q = MagicMock()
        q.is_correct.side_effect = lambda answer: answer == "42"
        q.correct_answer = "42"
        q.choices = ["42", "43", "44", "45"]
        q.question = "What's the answer to life?"
        return q

    # Monkeypatching the function to return the mock instead of calling the API
    monkeypatch.setattr(trivia_question, "get_random_trivia_question", _mock)


@pytest.fixture
def game(mock_get_random_trivia_question):
    """Create a TriviaGame instance after mocking is in place."""
    from trivia_game import TriviaGame  # Delay import until after monkeypatch
    st.session_state["selected_team"] = 1
    tg = TriviaGame(team_id=1)
    return tg


# ----- Tests -----


def test_initial_game_state(game):
    """Test the initial game state after initializing the TriviaGame."""
    assert st.session_state["pitches"] == 1
    assert st.session_state["strikes"] == 0
    assert st.session_state["bases"] == 0
    assert st.session_state["status"] == "At bat..."


def test_new_question(game):
    """Test that a new question is properly loaded."""
    initial_pitches = st.session_state["pitches"]
    game.new_question()  # Load new question
    assert st.session_state["pitches"] == initial_pitches + 1
    assert st.session_state[game.submit_key] is False
    assert st.session_state[game.process_key] is False


def test_next_pitch(game):
    """Test the transition to the next pitch."""
    game.next_pitch()
    assert game.question_key not in st.session_state
    assert game.submit_key not in st.session_state
    assert game.process_key not in st.session_state


def test_game_over_strikes(game):
    """Test the game-over condition based on strikes."""
    st.session_state["strikes"] = 3
    assert game.is_game_over() is True
    st.session_state["strikes"] = 2
    assert game.is_game_over() is False


def test_game_over_pitches(game):
    """Test the game-over condition based on pitches."""
    st.session_state["pitches"] = 5
    assert game.is_game_over() is True
    st.session_state["pitches"] = 4
    assert game.is_game_over() is False


def test_finalize_status_strikes(game):
    """Test the final status when game is over due to strikes."""
    st.session_state["strikes"] = 3
    game.finalize_status()
    assert st.session_state["status"] == "Three Strikes - You're OUT!"


def test_finalize_status_bases(game):
    """Test the final status based on number of bases."""
    st.session_state["strikes"] = 0
    status_map = {
        0: "Game Over!",
        1: "Single! You got 1 correct!",
        2: "Double! You got 2 correct!",
        3: "Triple! You got 3 correct!",
        4: "Home Run! You got 4 correct!",
        5: "Grand Slam! All 5 correct!",
    }

    for bases, expected_status in status_map.items():
        st.session_state["bases"] = bases
        game.finalize_status()
        assert st.session_state["status"] == expected_status

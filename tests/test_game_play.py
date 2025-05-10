import pytest
import streamlit as st
from unittest import mock
from trivia_game import st_game_play


# Fixture: returns mocked team and question
@pytest.fixture
def mock_team_and_question():
    mock_team = {'id': 1, 'name': 'Team A'}
    mock_question = mock.Mock()
    mock_question.question = "What is 2 + 2?"
    mock_question.choices = ["3", "4", "5"]
    mock_question.correct_answer = "4"
    mock_question.is_correct.return_value = True
    mock_question.image_url = "https://example.com/image.jpg"
    return mock_team, mock_question


def test_st_game_play(mock_team_and_question, mocker):
    mock_team, mock_question = mock_team_and_question

    # Initialize session state for game start
    mocker.patch.dict(
        st.session_state,
        {
            'selected_team': 1,
            'pitches': 0,
            'strikes': 0,
            'bases': 0,
            'status': "At bat...",
        }
    )

    # Mock database and question function calls
    mocker.patch('database.get_team_by_id', return_value=mock_team)
    mocker.patch('trivia_game.get_random_trivia_question',
                 return_value=mock_question)

    # Track session-based Submit and Next Pitch
    def button_side_effect(label, *args, **kwargs):
        if (label == "Submit" and not
                st.session_state.get('submitted_1', False)):
            return True  # Simulate clicking "Submit" once
        if label == "Next Pitch":
            return True  # Simulate clicking "Next Pitch"
        return False

    mocker.patch('streamlit.button', side_effect=button_side_effect)
    mocker.patch('streamlit.radio', return_value="4")
    mocker.patch('streamlit.image')
    mocker.patch('streamlit.rerun', side_effect=lambda: None)

    # Simulate first round with "Submit"
    st_game_play()

    assert st.session_state['pitches'] == 1
    assert st.session_state['bases'] == 1
    assert st.session_state['strikes'] == 0
    assert st.session_state['status'] == "At bat..."

    # Simulate "Next Pitch" round
    st_game_play()

    # Confirm session state is still consistent
    assert st.session_state['pitches'] == 2
    assert st.session_state['bases'] == 2
    assert st.session_state['strikes'] == 0
    assert st.session_state['status'] == "At bat..."

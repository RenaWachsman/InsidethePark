import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from ai import get_teams_and_players, ai_bot
import streamlit as st
from types import SimpleNamespace


@pytest.fixture(autouse=True)
def reset_streamlit_session():
    st.session_state.clear()


# Mocking sqlite3 to avoid using an actual database
@pytest.fixture
def mock_sqlite3():
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


# Test get_teams_and_players function
def test_get_teams_and_players(mock_sqlite3):
    # Prepare mock return value for the SQL query
    mock_df = pd.DataFrame({
        'team_name': ['Team A', 'Team B', 'Team A'],
        'player_name': ['Player 1', 'Player 2', 'Player 3']
    })
    # Mock the behavior of pd.read_sql_query
    with patch("pandas.read_sql_query", return_value=mock_df):
        teams_and_players = get_teams_and_players()
        expected_output = (
            "Team: Team A, Player: Player 1\n"
            "Team: Team B, Player: Player 2\n"
            "Team: Team A, Player: Player 3"
        )

        actual_output = ''.join(sorted(teams_and_players.splitlines()))
        expected_output = ''.join(sorted(expected_output.splitlines()))
        assert actual_output == expected_output


@patch("streamlit.chat_input")
@patch("streamlit.chat_message")
@patch("openai.AzureOpenAI")
def test_ai_bot(mock_azure_openai_class, mock_chat_message, mock_chat_input):
    # Setup mock client
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Sure, I can help with that!"
                )
            )
        ]
    )
    mock_azure_openai_class.return_value = mock_client

    mock_chat_input.return_value = "Tell me about Team A"

    with patch.dict("streamlit.session_state", {
        "openai_model": "gpt-4-turbo",
        "messages": [
            {
                "role": "assistant",
                "content": (
                    "🧑‍⚖️ *HI! I am a MLB Chat Bot Umpire. "
                    "Do you have any baseball questions?*"
                )
            }
        ]
    }, clear=True):
        # Run
        ai_bot(client=mock_client)

        # Assert chat history updated
        assert len(st.session_state["messages"]) == 3
        assert st.session_state["messages"][1] == {
            "role": "user",
            "content": "Tell me about Team A"
        }
        assert st.session_state["messages"][2] == {
            "role": "assistant",
            "content": "Sure, I can help with that!"
        }

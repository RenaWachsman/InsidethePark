import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import app
import pandas as pd


@pytest.fixture(autouse=True)
def reset_st_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()


def test_sidebar_menu_sets_session_state(mocker):
    mock_option_menu = mocker.patch("app.option_menu",
                                    return_value="Choose a Team")
    with patch.object(st, "sidebar"), \
         patch.object(st, "set_page_config"), \
         patch.object(st, "markdown"):
        st.session_state["menu_option"] = "Choose a Team"
        app.selected_sidebar = mock_option_menu()
        assert app.selected_sidebar == "Choose a Team"
        assert st.session_state["menu_option"] == "Choose a Team"


def test_team_selection_sets_team_id(mocker):
    teams_df = MagicMock()
    teams_df.iterrows.return_value = iter([
        (0, {'name': 'Yankees', 'id': 1})
    ])
    mocker.patch("app.get_all_teams", return_value=teams_df)
    mocker.patch("app.st.selectbox", return_value="Yankees")
    mocker.patch("app.st.rerun")

    app.choosing_team()
    assert st.session_state["selected_team"] == 1


def test_get_selected_team_prompts_if_none(mocker):
    mock_prompt = mocker.patch("app.choosing_team")
    st.session_state.clear()
    app.get_selected_team()
    mock_prompt.assert_called_once()


def test_fetch_player_info(mocker):
    mock_get_player_info = mocker.patch(
        "app.get_player_info", return_value={"idPlayer": 1}
    )
    result = app.fetch_player_info("John Doe")
    assert result["idPlayer"] == 1
    mock_get_player_info.assert_called_once_with("John Doe")


def test_team_info_page_with_valid_team(mocker):
    st.session_state["menu_option"] = "Team Info"
    st.session_state["selected_team"] = 1

    mocker.patch(
        "app.get_team_by_id",
        return_value={
            "name": "Yankees",
            "stadium": "Yankee Stadium",
            "stadium_addr": "NY",
            "phone": "123",
            "team_ext": "nyy"
        }
    )

    mocker.patch.multiple(
        st,
        subheader=MagicMock(),
        write=MagicMock(),
        markdown=MagicMock(),
        stop=MagicMock()
    )
    app.get_selected_team = lambda: 1
    app.team = app.get_team_by_id(1)
    assert app.team["name"] == "Yankees"


def test_get_to_know_players_page_rendering(mocker):
    st.session_state["menu_option"] = "Get to Know the Players"
    st.session_state["selected_team"] = 1
    st.session_state["player_details_shown"] = {}

    mocker.patch("app.get_team_by_id", return_value={"name": "Yankees"})
    mocker.patch(
        "app.get_players_by_team_id",
        return_value=pd.DataFrame([{
            "name": "John Doe",
            "jersey_number": 12,
            "headshot_url": "url"
        }])
    )
    mocker.patch("app.fetch_player_info", return_value={"idPlayer": 1})
    mocker.patch("app.fetch_player_honors", return_value=[])
    mocker.patch("app.fetch_player_teams", return_value=[])

    mocker.patch.multiple(
        st,
        subheader=MagicMock(),
        write=MagicMock(),
        expander=MagicMock(),
        columns=lambda x: [MagicMock() for _ in range(x)]
    )

    app.get_selected_team = lambda: 1
    app.get_selected_team()


def test_trivia_page_calls_game_play(mocker):
    st.session_state["menu_option"] = "Team Trivia"
    st.session_state["selected_team"] = 1

    mock_game_play = mocker.patch("app.st_game_play")
    app.st_game_play()
    mock_game_play.assert_called()


def test_ask_the_ump_page_calls_ai_bot(mocker):
    st.session_state["menu_option"] = "Ask the Ump"
    mock_bot = mocker.patch("app.ai_bot")
    app.ai_bot()
    mock_bot.assert_called()


def test_data_page_calls_visualizations(mocker):
    st.session_state["menu_option"] = "MLB Data"
    mocker.patch("app.st.radio", return_value="📍 MLB Stadium Map")
    mock_map = mocker.patch("app.stadium_map")
    app.stadium_map("mock_conn")
    mock_map.assert_called()

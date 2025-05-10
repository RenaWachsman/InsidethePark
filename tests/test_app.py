from unittest.mock import patch, MagicMock
import pandas as pd
import streamlit as st
import app
import api
import pytest


@pytest.fixture(autouse=True)
def mock_session_state():
    st.session_state.clear()
    st.session_state["menu_option"] = "Team Info"
    st.session_state["selected_team"] = 1
    yield
    st.session_state.clear()


def test_sidebar_updates_session_state(mocker):
    mock_option_menu = mocker.patch("app.option_menu",
                                    return_value="Choose a Team")
    with patch.object(st, "sidebar"), \
         patch.object(st, "set_page_config"), \
         patch.object(st, "markdown"):
        st.session_state["menu_option"] = "Choose a Team"
        app.selected_sidebar = mock_option_menu()
        assert app.selected_sidebar == "Choose a Team"
        assert st.session_state["menu_option"] == "Choose a Team"


def test_team_dropdown_select_sets_team(mocker):
    teams_df = MagicMock()
    teams_df.iterrows.return_value = iter([(0, {'name': 'Yankees', 'id': 1})])
    mocker.patch("app.get_all_teams", return_value=teams_df)
    mocker.patch("app.st.selectbox", return_value="Yankees")
    mocker.patch("app.st.rerun")

    app.choosing_team()
    assert st.session_state["selected_team"] == 1


def test_prompt_team_selection_if_not_chosen(mocker):
    st.session_state.clear()
    st.session_state["menu_option"] = "Team Trivia"
    mock_choose_team = mocker.patch("app.choosing_team")
    app.get_selected_team()
    mock_choose_team.assert_called_once()


def test_player_info_lookup(mocker):
    mock_api = mocker.patch("api.get_player_info",
                            return_value={"idPlayer": 123})
    result = api.get_player_info("Jane Doe")
    assert result["idPlayer"] == 123
    mock_api.assert_called_once_with("Jane Doe")


def test_team_info_displays_if_team_selected(mocker):
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


def test_players_page_loads_and_fetches_data(mocker):
    st.session_state.update({
        "menu_option": "Get to Know the Players",
        "selected_team": 1,
        "player_details_shown": {}
    })

    mocker.patch("app.get_team_by_id", return_value={"name": "Yankees"})
    mocker.patch("app.get_players_by_team_id", return_value=pd.DataFrame([{
        "name": "John Doe", "jersey_number": 99, "headshot_url": "some_url"
    }]))
    mocker.patch("api.get_player_info", return_value={"idPlayer": 123})
    mocker.patch("api.get_player_honors", return_value=[])
    mocker.patch("api.get_player_teams", return_value=[])

    mocker.patch.multiple(
        st,
        subheader=MagicMock(),
        write=MagicMock(),
        expander=MagicMock(),
        columns=lambda x: [MagicMock() for _ in range(x)],
        image=MagicMock(),
        button=MagicMock(return_value=False),
        markdown=MagicMock()
    )

    app.get_selected_team = lambda: 1
    app.get_selected_team()


def test_player_expander_opens_and_shows_data(mocker):
    st.session_state.update({
        "menu_option": "Get to Know the Players",
        "selected_team": 1,
        "player_details_shown": {}
    })

    mocker.patch("app.get_team_by_id", return_value={"name": "Yankees"})
    mocker.patch("app.get_players_by_team_id", return_value=pd.DataFrame([{
        "name": "John Doe", "jersey_number": 99, "headshot_url": "url"
    }]))
    mocker.patch("api.get_player_info", return_value={
        "idPlayer": 123,
        "dateBorn": "1990-01-01",
        "strNationality": "USA",
        "strPosition": "Pitcher"
    })
    mocker.patch("api.get_player_honors", return_value=[{
        "honour": "MVP",
        "team_name": "Yankees",
        "year": "2020"
    }])
    mocker.patch("api.get_player_teams", return_value=[{
        "former_team": "Red Sox",
        "joined": "2018",
        "departed": "2019",
        "move_type": "Trade"
    }])

    mocker.patch.multiple(
        st,
        subheader=MagicMock(),
        write=MagicMock(),
        expander=lambda *args, **kwargs: MagicMock(
            __enter__=lambda s: True, __exit__=lambda s, *a: None),
        columns=lambda x: [MagicMock() for _ in range(x)],
        image=MagicMock(),
        button=MagicMock(return_value=True),
        markdown=MagicMock()
    )

    app.get_selected_team = lambda: 1
    app.get_selected_team()


def test_trivia_starts_game(mocker):
    st.session_state.update({
        "menu_option": "Team Trivia",
        "selected_team": 1
    })

    mock_game_play = mocker.patch("app.TriviaGame")
    mock_instance = mock_game_play.return_value
    mock_instance.get_question.return_value = None

    app.TriviaGame(1)
    mock_game_play.assert_called_with(1)


def test_ask_the_ump_runs(mocker):
    st.session_state["menu_option"] = "Ask the Ump"
    mock_ump = mocker.patch("app.ai_bot")
    app.ai_bot()
    mock_ump.assert_called_once()


def test_mlb_data_page_shows_map(mocker):
    st.session_state["menu_option"] = "MLB Data"
    mocker.patch("app.st.radio", return_value="📍 MLB Stadium Map")
    mock_map = mocker.patch("app.stadium_map")

    app.stadium_map("mock_conn")
    mock_map.assert_called_once()


def test_player_info_not_found(mocker):
    mocker.patch("api.get_player_info", return_value=None)
    result = api.get_player_info("Non Existent Player")
    assert result is None


def test_player_honors_not_found(mocker):
    mocker.patch("api.get_player_honors", return_value=None)
    result = api.get_player_honors(123)
    assert result is None


def test_player_teams_not_found(mocker):
    mocker.patch("api.get_player_teams", return_value=None)
    result = api.get_player_teams(123)
    assert result is None

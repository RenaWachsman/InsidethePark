from unittest.mock import patch, MagicMock
import requests
from api import get_player_info, get_player_teams, get_player_honors
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Test for get_player_info
@patch('requests.get')
def test_get_player_info_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "player": [{
            "idPlayer": "12345",
            "strNationality": "USA",
            "dateBorn": "1990-01-01",
            "strPosition": "Pitcher",
            "strSport": "Baseball"
        }]
    }
    mock_get.return_value = mock_response

    player_info = get_player_info("John Doe")

    assert player_info["idPlayer"] == "12345"
    assert player_info["strNationality"] == "USA"
    assert player_info["dateBorn"] == "1990-01-01"
    assert player_info["strPosition"] == "Pitcher"


@patch('requests.get')
def test_get_player_info_no_player_found(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"player": []}
    mock_get.return_value = mock_response

    player_info = get_player_info("Nonexistent Player")
    assert player_info is None


@patch('requests.get')
def test_get_player_info_not_baseball(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "player": [{
            "idPlayer": "12345",
            "strNationality": "USA",
            "dateBorn": "1990-01-01",
            "strPosition": "Basketball Player",
            "strSport": "Basketball"
        }]
    }
    mock_get.return_value = mock_response

    player_info = get_player_info("John Doe")
    assert player_info is None


@patch('requests.get')
def test_get_player_teams_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "formerteams": [{
            "strPlayer": "John Doe",
            "strFormerTeam": "Team A",
            "strMoveType": "Transfer",
            "strJoined": "2015-01-01",
            "strDeparted": "2017-01-01"
        }]
    }
    mock_get.return_value = mock_response

    player_teams = get_player_teams("12345")

    assert len(player_teams) == 1
    assert player_teams[0]["player_name"] == "John Doe"
    assert player_teams[0]["former_team"] == "Team A"
    assert player_teams[0]["move_type"] == "Transfer"
    assert player_teams[0]["joined"] == "2015-01-01"
    assert player_teams[0]["departed"] == "2017-01-01"


@patch('requests.get')
def test_get_player_teams_no_teams(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"formerteams": []}
    mock_get.return_value = mock_response

    player_teams = get_player_teams("12345")
    assert player_teams == []


@patch('requests.get')
def test_get_player_honors_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "honours": [{
            "strPlayer": "John Doe",
            "strTeam": "Team A",
            "strHonour": "MVP",
            "strSeason": "2016"
        }]
    }
    mock_get.return_value = mock_response

    player_honors = get_player_honors("12345")

    assert len(player_honors) == 1
    assert player_honors[0]["player_name"] == "John Doe"
    assert player_honors[0]["team_name"] == "Team A"
    assert player_honors[0]["honour"] == "MVP"
    assert player_honors[0]["year"] == "2016"


@patch('requests.get')
def test_get_player_honors_no_honors(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"honours": []}
    mock_get.return_value = mock_response

    player_honors = get_player_honors("12345")
    assert player_honors == []


@patch('requests.get')
def test_get_player_info_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException
    player_info = get_player_info("John Doe")
    assert player_info is None


@patch('requests.get')
def test_get_player_teams_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException
    player_teams = get_player_teams("12345")
    assert player_teams == []


@patch('requests.get')
def test_get_player_honors_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException
    player_honors = get_player_honors("12345")
    assert player_honors == []

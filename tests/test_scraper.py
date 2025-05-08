import pytest
from unittest.mock import patch, Mock
from scraper import scrape_teams, scrape_players

# Clean and consistent mock HTML for testing
MOCK_HTML_TEAMS = """
<html>
    <body>
        <div class="p-forge-list-item">
            <a href="/team1"></a>
            <img class="p-forge-logo" src="//logo1.com" />
            <h2 class="p-heading__text">Team 1</h2>
            <div class="p-wysiwyg">
                <p>Stadium 1<br>Address 1<br>Address Line 2<br>(123) 456-7890
                </p>
            </div>
        </div>
        <div class="p-forge-list-item">
            <a href="/team2"></a>
            <img class="p-forge-logo" src="//logo2.com" />
            <h2 class="p-heading__text">Team 2</h2>
            <div class="p-wysiwyg">
                <p>Stadium 2<br>Address 2<br>Address Line 2<br>(713) 259-8000
                </p>
            </div>
        </div>
    </body>
</html>
"""

MOCK_HTML_PLAYERS = """
<html>
    <body>
        <table>
            <tr>
                <td class="player-thumb">
                    <img src="https://www.mlb.com/player1.jpg"/>
                </td>
                <td class="info">
                    <a>Player 1</a>
                </td>
                <td>
                    <span class="jersey">99</span>
                </td>
            </tr>
            <tr>
                <td class="player-thumb">
                    <img src="https://www.mlb.com/player2.jpg"/>
                </td>
                <td class="info">
                    <a>Player 2</a>
                </td>
                <td>
                    <span class="jersey">23</span>
                </td>
            </tr>
        </table>
    </body>
</html>
"""


@patch('requests.get')
def test_scrape_teams(mock_get):
    mock_response = Mock()
    mock_response.content = MOCK_HTML_TEAMS
    mock_get.return_value = mock_response

    url = "https://www.mlb.com/teams"
    result = scrape_teams(url)

    assert len(result) == 2
    assert result[0]['team_name'] == 'Team 1'
    assert result[0]['logo_url'] == 'https://logo1.com'
    assert result[0]['stadium'] == 'Stadium 1'
    assert result[0]['stadium_addr'] == 'Address 1 Address Line 2'
    assert result[0]['phone'] == '(123) 456-7890'
    assert result[0]['team_ext'] == '/team1'

    assert result[1]['team_name'] == 'Team 2'
    assert result[1]['logo_url'] == 'https://logo2.com'
    assert result[1]['stadium'] == 'Stadium 2'
    assert result[1]['stadium_addr'] == 'Address 2 Address Line 2'
    assert result[1]['phone'] == '(713) 259-8000'
    assert result[1]['team_ext'] == '/team2'


@patch('requests.get')
def test_scrape_players(mock_get):
    mock_response = Mock()
    mock_response.content = MOCK_HTML_PLAYERS
    mock_get.return_value = mock_response

    team_ext = "team1"
    result = scrape_players(team_ext)

    assert len(result) == 2
    assert result[0]['player_name'] == 'Player 1'
    assert result[0]['jersey_number'] == '99'
    assert result[0]['headshot_url'] == 'https://www.mlb.com/player1.jpg'

    assert result[1]['player_name'] == 'Player 2'
    assert result[1]['jersey_number'] == '23'
    assert result[1]['headshot_url'] == 'https://www.mlb.com/player2.jpg'


if __name__ == "__main__":
    pytest.main()

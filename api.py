import requests

# API URL for TheSportsDB (no trailing slash)
API_URL = "https://www.thesportsdb.com/api/v1/json/3"


def get_player_info(player_name):
    """Fetch minimal player information."""
    try:
        formatted_player_name = player_name.replace(" ", "_")
        ext = "searchplayers.php?p="
        response = requests.get(f"{API_URL}/{ext}{formatted_player_name}")
        response.raise_for_status()

        player_info = response.json()

        if not player_info.get("player"):
            return None

        player = player_info["player"][0]

        if player.get("strSport") != "Baseball":
            return None

        return {
            "idPlayer": player.get("idPlayer"),
            "strNationality": player.get("strNationality"),
            "dateBorn": player.get("dateBorn"),
            "strPosition": player.get("strPosition")
        }

    except requests.exceptions.RequestException:
        return None


def get_player_teams(player_id):
    """Fetch the list of former teams for a given player based on player ID."""
    try:
        ext = "lookupformerteams.php?id="
        response = requests.get(f"{API_URL}/{ext}{player_id}")
        response.raise_for_status()

        player_info = response.json()

        if not player_info.get("formerteams"):
            return []

        return [
            {
                "player_name": team.get('strPlayer'),
                "former_team": team.get('strFormerTeam'),
                "move_type": team.get('strMoveType'),
                "joined": team.get('strJoined'),
                "departed": team.get('strDeparted')
            }
            for team in player_info['formerteams']
        ]

    except requests.exceptions.RequestException:
        return []


def get_player_honors(player_id):
    """Fetch honors and achievements for the player based on player ID."""
    try:
        ext = "lookuphonours.php?id="
        response = requests.get(f"{API_URL}/{ext}{player_id}")
        response.raise_for_status()

        player_info = response.json()

        if not player_info.get("honours"):
            return []

        return [
            {
                "player_name": honor.get('strPlayer'),
                "team_name": honor.get('strTeam'),
                "honour": honor.get('strHonour'),
                "year": honor.get('strSeason')
            }
            for honor in player_info['honours']
        ]

    except requests.exceptions.RequestException:
        return []

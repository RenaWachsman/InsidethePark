# This Module runs the Scrape
import requests
from bs4 import BeautifulSoup

""" Scrape team and team details from mlb.com/teams"""


def scrape_teams(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    teams_data = []

    all_teams = soup.find_all('div', class_='p-forge-list-item')

    for team in all_teams:
        link_tag = team.find('a', href=True)
        team_href = link_tag['href'] if link_tag else None

        logo_tag = team.find('img', class_='p-forge-logo')
        logo_url = logo_tag['src'] if logo_tag else None
        if logo_url and logo_url.startswith("//"):
            logo_url = "https:" + logo_url

        name_tag = team.find('h2', class_='p-heading__text')
        team_name = name_tag.get_text(strip=True) if name_tag else None

        stadium_div = team.find('div', class_='p-wysiwyg')
        stadium_name = None
        stadium_addr = None
        stadium_addr2 = None
        phone = None
        if stadium_div:
            paragraphs = stadium_div.find_all('p')
            for p in paragraphs:
                lines = p.get_text(separator='\n').splitlines()
                if lines:
                    stadium_name = lines[0].strip().strip('"')
                    stadium_addr = lines[1].strip().strip('"')
                    stadium_addr2 = lines[2].strip().strip('"')
                    phone = lines[3].strip().strip('"')

        teams_data.append({
            'team_name': team_name,
            'logo_url': logo_url,
            'stadium': stadium_name,
            'stadium_addr': stadium_addr + " " + stadium_addr2,
            'phone': phone,
            'team_ext': team_href
        })

    return teams_data


"""For each team Scrape the Players from that teams Roster Page"""


def scrape_players(team_ext):
    page = requests.get(f"https://www.mlb.com/{team_ext}/roster")
    soup = BeautifulSoup(page.content, "html.parser")
    players_data = []

    all_players = soup.find_all('tr')
    for player in all_players:
        img_tag = player.select_one('td.player-thumb img')
        headshot_url = img_tag['src'] if img_tag else None

        name_tag = player.select_one('td.info a')
        name = name_tag.get_text(strip=True) if name_tag else None

        jersey_tag = player.select_one('span.jersey')
        jersey_number = jersey_tag.get_text(strip=True) if jersey_tag else None

        if name:
            players_data.append({
                'player_name': name,
                'jersey_number': jersey_number,
                'headshot_url': headshot_url
            })

    return players_data

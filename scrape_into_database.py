from scraper import scrape_teams
from database import create_db, insert_teams_and_players
from data_displays import add_lat_lng_columns, geocode_and_update_teams


def main():
    url = "https://www.mlb.com/team"
    teams_data = scrape_teams(url)

    conn = create_db()
    insert_teams_and_players(conn, teams_data)
    add_lat_lng_columns()
    geocode_and_update_teams()
    conn.close()


if __name__ == "__main__":
    main()

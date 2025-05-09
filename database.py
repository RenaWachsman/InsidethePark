import sqlite3
from scraper import scrape_players
import pandas as pd
import streamlit as st


def create_db(db_name="mlb.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            logo_url TEXT,
            stadium TEXT,
            stadium_addr TEXT,
            phone TEXT,
            team_ext TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            name TEXT,
            jersey_number TEXT,
            headshot_url TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    """)

    conn.commit()
    return conn


def insert_teams_and_players(conn, teams_data, player_scraper=scrape_players):
    cur = conn.cursor()

    for team in teams_data:
        cur.execute("""
            INSERT OR IGNORE INTO teams (name, logo_url, stadium, stadium_addr,
                                         phone, team_ext)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            team['team_name'], team['logo_url'], team['stadium'],
            team['stadium_addr'], team['phone'], team['team_ext']
        ))

        conn.commit()

        cur.execute("SELECT id FROM teams WHERE team_ext = ?",
                    (team['team_ext'],))
        team_id = cur.fetchone()[0]

        # Use the player_scraper function to scrape players
        players = player_scraper(team['team_ext'])

        for player in players:
            cur.execute("""
                INSERT INTO players (team_id, name, jersey_number,
                        headshot_url)
                VALUES (?, ?, ?, ?)
            """, (
                team_id,
                player['player_name'],
                player['jersey_number'],
                player['headshot_url']
            ))

        conn.commit()


def get_connection():
    return sqlite3.connect("mlb.db")


def get_all_teams():
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT id, name, logo_url, stadium, stadium_addr, phone, team_ext
            FROM teams ORDER BY name
        """, conn)


def get_team_by_id(team_id):
    with get_connection() as conn:
        team_id = int(team_id)  # Ensure input is an integer
        df = pd.read_sql_query(
            "SELECT * FROM teams WHERE id = ?", conn, params=(team_id,)
        )
        return df.iloc[0] if not df.empty else None


@st.cache_data
def get_players_by_team_id(team_id):
    """
    Get players for a team by team_id.
    """
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT name, jersey_number, headshot_url, team_id "
            "FROM players WHERE team_id = ?",
            conn, params=(team_id,)
        )


def get_team_name_by_id(team_id, conn=None):
    """
    Get team name by team_id.
    """
    if conn is None:
        conn = get_connection()

    with conn:
        df = pd.read_sql_query(
            "SELECT name FROM teams WHERE id = ?", conn, params=(team_id,)
        )
        return df.iloc[0]["name"] if not df.empty else "Unknown"

# This module creates 3 data displays
import sqlite3
from geopy.geocoders import Nominatim
from time import sleep
import streamlit as st
import pandas as pd

# First Data Display - map of the stadiums


def add_lat_lng_columns():
    """This function adds columns to the database"""
    conn = sqlite3.connect("mlb.db")
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE teams ADD COLUMN latitude REAL")
    except sqlite3.OperationalError as e:
        print(f"Column 'latitude' might already exist: {e}")
    try:
        cur.execute("ALTER TABLE teams ADD COLUMN longitude REAL")
    except sqlite3.OperationalError as e:
        print(f"Column 'longitude' might already exist: {e}")
    conn.commit()
    conn.close()


def geocode_and_update_teams():
    """Find the coordinates of the stadiums - Using geocolater"""
    geolocator = Nominatim(user_agent="mlb_app")
    conn = sqlite3.connect("mlb.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, stadium_addr FROM teams
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    teams = cur.fetchall()

    for team_id, address in teams:
        try:
            location = geolocator.geocode(address)
            if location:
                cur.execute(
                    "UPDATE teams SET latitude = ?, longitude = ? "
                    "WHERE id = ?",
                    (location.latitude, location.longitude, team_id)
                )
                print(f"Updated team {team_id} - {address}")
                sleep(1)  # Respect Nominatim usage policy
        except Exception as e:
            print(f"Error geocoding team {team_id} at '{address}': {e}")

    conn.commit()
    conn.close()


def stadium_map(conn):
    """This maps the stadiums on the map of the US"""
    df = pd.read_sql_query(
        "SELECT name, latitude, longitude FROM teams "
        "WHERE latitude IS NOT NULL AND longitude IS NOT NULL", conn
    )
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    st.map(df)


# Second Data Display- Jersey Distribution Bar Chart

def jersey_distribution(conn):
    """This function makes a bar chart of the jersey numbers """
    df = pd.read_sql_query("SELECT jersey_number FROM players", conn)
    df['jersey_number'] = pd.to_numeric(df['jersey_number'], errors='coerce')
    df = df.dropna()
    st.bar_chart(df['jersey_number'].value_counts().sort_index())

# Second Data Display- Players by Number Slider


def players_by_jersey(conn):
    """This function is a slider to see players by a specific jersey number """
    st.markdown("#### Select a jersey number:")
    jersey_number = st.slider("", 0, 99, 0)

    df_players = pd.read_sql_query(
        """
        SELECT players.name, players.jersey_number, players.headshot_url,
               teams.name AS team_name
        FROM players
        JOIN teams ON players.team_id = teams.id
        WHERE players.jersey_number = ?
        """,
        conn, params=(str(jersey_number),)
    )

    if df_players.empty:
        st.info(f"No players found with jersey number {jersey_number}.")
    else:
        st.markdown(f"##### Players wearing #{jersey_number}")
        cols = st.columns(4)
        for i, (_, row) in enumerate(df_players.iterrows()):
            with cols[i % 4]:
                st.image(row['headshot_url'], width=100)
                st.markdown(f"**{row['name']}**")
                st.caption(row['team_name'])

import sqlite3
import pytest
import pandas as pd
from database import (
    insert_teams_and_players,
    get_all_teams, get_team_by_id,
    get_players_by_team_id, get_team_name_by_id
)

# Sample data for tests
TEST_TEAMS = [{
    'team_name': 'Test Team',
    'logo_url': 'http://logo.test/logo.png',
    'stadium': 'Test Stadium',
    'stadium_addr': '123 Stadium Ln',
    'phone': '555-1234',
    'team_ext': 'testteam'
}]

TEST_PLAYERS = [{
    'player_name': 'Jane Doe',
    'jersey_number': '7',
    'headshot_url': 'http://image.test/player.png'
}]


@pytest.fixture
def in_memory_db():
    """Provide a fresh in-memory database with schema created."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Create schema
    cur.execute("""
        CREATE TABLE teams (
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
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            name TEXT,
            jersey_number TEXT,
            headshot_url TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_scraper(mocker):
    return mocker.Mock(return_value=TEST_PLAYERS)


def test_insert_teams_and_players(in_memory_db, mock_scraper):
    insert_teams_and_players(in_memory_db, TEST_TEAMS,
                             player_scraper=mock_scraper)
    cur = in_memory_db.cursor()

    cur.execute("SELECT * FROM teams")
    teams = cur.fetchall()
    assert len(teams) == 1
    assert teams[0][1] == 'Test Team'

    cur.execute("SELECT * FROM players")
    players = cur.fetchall()
    assert len(players) == 1
    assert players[0][2] == 'Jane Doe'


def test_get_team_name_by_id_with_conn(in_memory_db, mock_scraper):
    insert_teams_and_players(in_memory_db, TEST_TEAMS,
                             player_scraper=mock_scraper)
    name = get_team_name_by_id(1, conn=in_memory_db)
    assert name == "Test Team"


def test_get_team_name_by_id_unknown(in_memory_db):
    name = get_team_name_by_id(99, conn=in_memory_db)
    assert name == "Unknown"


def test_get_all_teams(monkeypatch, mock_scraper):
    def fake_conn():
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE teams (
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
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                name TEXT,
                jersey_number TEXT,
                headshot_url TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        """)
        conn.commit()
        insert_teams_and_players(conn, TEST_TEAMS, player_scraper=mock_scraper)
        return conn

    monkeypatch.setattr("database.get_connection", fake_conn)
    df = get_all_teams()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.iloc[0]['name'] == 'Test Team'


def test_get_team_by_id(monkeypatch, mock_scraper):
    def fake_conn():
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE teams (
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
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                name TEXT,
                jersey_number TEXT,
                headshot_url TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        """)
        conn.commit()
        insert_teams_and_players(conn, TEST_TEAMS, player_scraper=mock_scraper)
        return conn

    monkeypatch.setattr("database.get_connection", fake_conn)
    team = get_team_by_id(1)
    assert team['name'] == 'Test Team'


def test_get_players_by_team_id(monkeypatch, mock_scraper):
    def fake_conn():
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE teams (
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
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                name TEXT,
                jersey_number TEXT,
                headshot_url TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        """)
        conn.commit()
        insert_teams_and_players(conn, TEST_TEAMS, player_scraper=mock_scraper)
        return conn

    monkeypatch.setattr("database.get_connection", fake_conn)
    df = get_players_by_team_id(1)
    assert not df.empty
    assert df.iloc[0]['name'] == 'Jane Doe'

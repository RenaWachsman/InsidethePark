import sqlite3
import pytest
from unittest import mock
from data_displays import (
    add_lat_lng_columns,
    geocode_and_update_teams
)


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_mlb.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Create mock tables and insert sample data
    cur.execute("""
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY,
            name TEXT,
            stadium_addr TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    cur.execute("""
        INSERT INTO teams (id, name, stadium_addr) VALUES
        (1, 'Team A', '123 Main St, Anytown USA'),
        (2, 'Team B', '456 Elm St, Othertown USA')
    """)
    conn.commit()
    conn.close()
    return db_path


def test_add_lat_lng_columns(temp_db):
    # Simulate a DB without lat/lng columns
    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("CREATE TABLE test (id INTEGER)")
    conn.commit()
    conn.close()

    # Patch sqlite3.connect to use test DB
    with mock.patch(
        "sqlite3.connect",
        return_value=sqlite3.connect(temp_db)
    ):
        add_lat_lng_columns()

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(teams)")
    columns = [col[1] for col in cur.fetchall()]
    assert 'latitude' in columns
    assert 'longitude' in columns


def test_geocode_and_update_teams():
    mock_location = mock.Mock()
    mock_location.latitude = 40.0
    mock_location.longitude = -75.0

    with mock.patch("sqlite3.connect") as mock_connect, \
        mock.patch(
        "geopy.geocoders.Nominatim.geocode",
        return_value=mock_location
    ), \
            mock.patch("time.sleep"):

        # Set up mock connection and cursor
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate return from SELECT query
        mock_cursor.fetchall.return_value = [(1, "123 Fake Street")]

        # Call the function
        geocode_and_update_teams()

        # Check query was called
        called_queries = [
            call[0][0].strip()
            for call in mock_cursor.execute.call_args_list
        ]
        assert (
            "UPDATE teams SET latitude = ?, longitude = ? WHERE id = ?"
            in called_queries
        )

        # Check that commit was called
        mock_conn.commit.assert_called_once()

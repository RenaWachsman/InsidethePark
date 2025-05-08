from unittest import mock
from scrape_into_database import main


@mock.patch("scrape_into_database.geocode_and_update_teams")
@mock.patch("scrape_into_database.add_lat_lng_columns")
@mock.patch("scrape_into_database.insert_teams_and_players")
@mock.patch("scrape_into_database.create_db")
@mock.patch("scrape_into_database.scrape_teams")
def test_main(
    mock_scrape_teams,
    mock_create_db,
    mock_insert_teams_and_players,
    mock_add_lat_lng_columns,
    mock_geocode_and_update_teams,
):
    # Arrange
    fake_conn = mock.Mock()
    mock_create_db.return_value = fake_conn
    mock_scrape_teams.return_value = [{"name": "Yankees"}]

    # Act
    main()

    # Assert
    mock_scrape_teams.assert_called_once_with("https://www.mlb.com/team")
    mock_create_db.assert_called_once()
    mock_insert_teams_and_players.assert_called_once_with(
        fake_conn, [{"name": "Yankees"}])
    mock_add_lat_lng_columns.assert_called_once()
    mock_geocode_and_update_teams.assert_called_once()
    fake_conn.close.assert_called_once()

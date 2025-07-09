import pytest
from unittest.mock import patch, MagicMock
import json
import os

# Import the functions from the module to be tested
from src.manager.analysis_manager import (
    get_access_token,
    get_dps_rankings,
    parse_rankings_response,
    format_rankings_as_markdown,
    save_markdown_output,
    main,
    CLIENT_ID, # Import for testing main
    CLIENT_SECRET # Import for testing main
)

# Mock environment variables for consistent testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret"
    }):
        yield

# --- Tests for get_access_token ---

def test_get_access_token_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "mock_token"}
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response) as mock_post:
        token = get_access_token("mock_client_id", "mock_client_secret")
        assert token == "mock_token"
        mock_post.assert_called_once()

def test_get_access_token_invalid_credentials():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")

    with patch('requests.post', return_value=mock_response):
        token = get_access_token("invalid_client_id", "invalid_client_secret")
        assert token is None

def test_get_access_token_network_error():
    with patch('requests.post', side_effect=requests.exceptions.RequestException("Network error")):
        token = get_access_token("mock_client_id", "mock_client_secret")
        assert token is None

def test_get_access_token_json_decode_error():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response):
        token = get_access_token("mock_client_id", "mock_client_secret")
        assert token is None

def test_get_access_token_missing_env_vars():
    # Test when client_id or client_secret are None (e.g., not set in .env)
    token = get_access_token(None, "mock_client_secret")
    assert token is None
    token = get_access_token("mock_client_id", None)
    assert token is None

# --- Tests for get_dps_rankings ---

def test_get_dps_rankings_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"worldData": {"encounter": {"name": "Test Boss", "characterRankings": "{\"rankings\": [{\"name\": \"Player1\"}]}"}}}} # Note: characterRankings is a JSON string
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response) as mock_post:
        rankings = get_dps_rankings("mock_token", 123, 5, "dps")
        assert rankings is not None
        assert "data" in rankings
        mock_post.assert_called_once()

def test_get_dps_rankings_no_token():
    rankings = get_dps_rankings(None, 123, 5, "dps")
    assert rankings is None

def test_get_dps_rankings_network_error():
    with patch('requests.post', side_effect=requests.exceptions.RequestException("Network error")):
        rankings = get_dps_rankings("mock_token", 123, 5, "dps")
        assert rankings is None

def test_get_dps_rankings_http_error():
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

    with patch('requests.post', return_value=mock_response):
        rankings = get_dps_rankings("mock_token", 123, 5, "dps")
        assert rankings is None

def test_get_dps_rankings_json_decode_error():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response):
        rankings = get_dps_rankings("mock_token", 123, 5, "dps")
        assert rankings is None

# --- Tests for parse_rankings_response ---

def test_parse_rankings_response_success():
    api_response = {
        "data": {
            "worldData": {
                "encounter": {
                    "name": "Test Boss",
                    "characterRankings": '{"rankings": [{"name": "Player1", "amount": 100.0}]}'
                }
            }
        }
    }
    parsed_data = parse_rankings_response(api_response)
    assert parsed_data is not None
    assert parsed_data["encounter_name"] == "Test Boss"
    assert len(parsed_data["rankings"]) == 1
    assert parsed_data["rankings"][0]["name"] == "Player1"

def test_parse_rankings_response_missing_encounter_data():
    api_response = {"data": {"worldData": {}}}
    parsed_data = parse_rankings_response(api_response)
    assert parsed_data is None

def test_parse_rankings_response_missing_character_rankings():
    api_response = {"data": {"worldData": {"encounter": {"name": "Test Boss"}}}}
    parsed_data = parse_rankings_response(api_response)
    assert parsed_data is None

def test_parse_rankings_response_invalid_json_string():
    api_response = {
        "data": {
            "worldData": {
                "encounter": {
                    "name": "Test Boss",
                    "characterRankings": "invalid json string"
                }
            }
        }
    }
    parsed_data = parse_rankings_response(api_response)
    assert parsed_data is None

# --- Tests for format_rankings_as_markdown ---

def test_format_rankings_as_markdown_success():
    rankings_data = [
        {"rank": 1, "name": "PlayerA", "amount": 12345.67, "class": "Warrior", "spec": "Fury", "guild": {"name": "GuildA"}, "server": {"name": "ServerA"}, "report": {"code": "abc1"}},
        {"rank": 2, "name": "PlayerB", "amount": 9876.54, "class": "Mage", "spec": "Fire", "guild": {"name": "GuildB"}, "server": {"name": "ServerB"}, "report": {"code": "def2"}}
    ]
    markdown = format_rankings_as_markdown("Test Encounter", rankings_data)
    assert "## Top 2 DPS Rankings for Test Encounter (Mythic)" in markdown
    assert "| Rank | Player | DPS | Class | Spec | Guild | Server | Report |" in markdown
    assert "|---|---|---|---|---|---|---|---|" in markdown
    assert "| 1 | PlayerA | 12345.67 | Warrior | Fury | GuildA | ServerA | abc1 |" in markdown
    assert "| 2 | PlayerB | 9876.54 | Mage | Fire | GuildB | ServerB | def2 |" in markdown

def test_format_rankings_as_markdown_empty_rankings():
    markdown = format_rankings_as_markdown("Test Encounter", [])
    assert markdown == "No rankings to display.\n"

# --- Tests for save_markdown_output ---

def test_save_markdown_output_success(tmp_path):
    test_content = "# Test Markdown\n\nThis is a test."
    test_filename = tmp_path / "test_rankings.md"
    save_markdown_output(test_content, str(test_filename))
    assert test_filename.read_text(encoding="utf-8") == test_content

def test_save_markdown_output_io_error():
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        # We expect a print statement for the error, so capture stdout
        with patch('builtins.print') as mock_print:
            save_markdown_output("some content", "/nonexistent/path/file.md")
            mock_print.assert_called_with("Error saving markdown output to file: Permission denied")

# --- Tests for main function ---

@patch('src.manager.analysis_manager.get_access_token')
@patch('src.manager.analysis_manager.get_dps_rankings')
@patch('src.manager.analysis_manager.parse_rankings_response')
@patch('src.manager.analysis_manager.format_rankings_as_markdown')
@patch('src.manager.analysis_manager.save_markdown_output')
@patch('src.manager.analysis_manager.CLIENT_ID', "mock_client_id")
@patch('src.manager.analysis_manager.CLIENT_SECRET', "mock_client_secret")
def test_main_success(
    mock_save_markdown_output,
    mock_format_rankings_as_markdown,
    mock_parse_rankings_response,
    mock_get_dps_rankings,
    mock_get_access_token
):
    mock_get_access_token.return_value = "mock_token"
    mock_get_dps_rankings.return_value = {"data": {"worldData": {"encounter": {"name": "Test Boss", "characterRankings": '{"rankings": []}'}}}} # Simplified response
    mock_parse_rankings_response.return_value = {"encounter_name": "Test Boss", "rankings": []}
    mock_format_rankings_as_markdown.return_value = "# Mock Markdown"

    main()

    mock_get_access_token.assert_called_once_with("mock_client_id", "mock_client_secret")
    mock_get_dps_rankings.assert_called_once_with("mock_token", 3016, 5, "dps")
    mock_parse_rankings_response.assert_called_once()
    mock_format_rankings_as_markdown.assert_called_once_with("Test Boss", [])
    mock_save_markdown_output.assert_called_once_with("# Mock Markdown")

@patch('src.manager.analysis_manager.get_access_token', return_value=None)
@patch('builtins.print')
def test_main_no_access_token(mock_print):
    main()
    mock_print.assert_any_call("Getting access token...")
    mock_print.assert_any_call("Failed to obtain access token. Please check your credentials.")

@patch('src.manager.analysis_manager.get_access_token', return_value="mock_token")
@patch('src.manager.analysis_manager.get_dps_rankings', return_value=None)
@patch('builtins.print')
def test_main_no_dps_rankings(mock_print):
    main()
    mock_print.assert_any_call("Access token received. Fetching rankings...")
    mock_print.assert_any_call("Could not retrieve rankings data from the API.")

@patch('src.manager.analysis_manager.get_access_token', return_value="mock_token")
@patch('src.manager.analysis_manager.get_dps_rankings', return_value={'data': {}} ) # Invalid API response
@patch('src.manager.analysis_manager.parse_rankings_response', return_value=None)
@patch('builtins.print')
def test_main_parse_rankings_failure(mock_print):
    main()
    mock_print.assert_any_call("Failed to parse rankings data.")

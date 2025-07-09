import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
CLIENT_ID: Optional[str] = os.getenv("client_id")
CLIENT_SECRET: Optional[str] = os.getenv("client_secret")

# API Endpoints
TOKEN_URL: str = "https://www.warcraftlogs.com/oauth/token"
API_URL: str = "https://www.warcraftlogs.com/api/v2/client"

# Encounter Details for the latest final boss (Gallywix - Mythic)
# You can find these IDs by browsing the Warcraft Logs website.
# The URL for the rankings page will contain the encounter ID.
ENCOUNTER_ID: int = 3016  # Gallywix
DIFFICULTY: int = 5       # 5 corresponds to Mythic difficulty
METRIC: str = "dps"       # We want to get DPS rankings

def get_access_token(client_id: Optional[str], client_secret: Optional[str]) -> Optional[str]:
    """
    Authenticates with the Warcraft Logs API to get an access token.

    Args:
        client_id: The client ID for the Warcraft Logs API.
        client_secret: The client secret for the Warcraft Logs API.

    Returns:
        The access token string if successful, None otherwise.
    """
    if not client_id or not client_secret:
        print("Client ID or Client Secret not found in environment variables.")
        return None

    try:
        data: Dict[str, str] = {"grant_type": "client_credentials"}
        auth: tuple[str, str] = (client_id, client_secret)
        response: requests.Response = requests.post(TOKEN_URL, data=data, auth=auth)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        if e.response:
            print(f"Response content: {e.response.text}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from token response.")
        return None

def get_dps_rankings(token: str, encounter_id: int, difficulty: int, metric: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the top DPS rankings for a specific encounter from Warcraft Logs API.

    Args:
        token: The access token for the Warcraft Logs API.
        encounter_id: The ID of the encounter (boss).
        difficulty: The difficulty of the encounter (e.g., 5 for Mythic).
        metric: The metric to rank by (e.g., "dps", "hps").

    Returns:
        A dictionary containing the API response data, or None if an error occurs.
    """
    if not token:
        print("Cannot fetch rankings without an access token.")
        return None

    # GraphQL query to fetch the rankings
    query: str = """
        query($encounterID: Int!, $difficulty: Int!, $metric: CharacterRankingMetricType!) {
          worldData {
            encounter(id: $encounterID) {
              name
              characterRankings(metric: $metric, difficulty: $difficulty)
            }
          }
        }
        """

    variables: Dict[str, Any] = {
        "encounterID": encounter_id,
        "difficulty": difficulty,
        "metric": metric
    }

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response: requests.Response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rankings: {e}")
        if e.response:
            print(f"Response content: {e.response.text}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from rankings response.")
        return None

def parse_rankings_response(api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parses the raw API response to extract encounter name and character rankings.

    Args:
        api_response: The raw dictionary response from the Warcraft Logs API.

    Returns:
        A dictionary containing 'encounter_name' and 'rankings' (list of dicts),
        or None if the expected data structure is not found.
    """
    encounter_data: Dict[str, Any] = api_response.get('data', {}).get('worldData', {}).get('encounter', {})
    if not encounter_data:
        print("Could not find encounter data in the API response.")
        return None

    encounter_name: Optional[str] = encounter_data.get('name')
    # The 'characterRankings' field returns a JSON string that needs to be parsed.
    rankings_json_string: Optional[str] = encounter_data.get('characterRankings')

    if not rankings_json_string:
        print("No character rankings found in the API response.")
        return None

    try:
        # Parse the JSON string within 'characterRankings'
        parsed_rankings: Dict[str, Any] = json.loads(rankings_json_string)
        # Get the list of ranks and limit to the top 10.
        ranks: List[Dict[str, Any]] = parsed_rankings.get('rankings', [])[:10]
        return {"encounter_name": encounter_name, "rankings": ranks}
    except json.JSONDecodeError:
        print("Error decoding characterRankings JSON string.")
        return None

def format_rankings_as_markdown(encounter_name: str, rankings: List[Dict[str, Any]]) -> str:
    """
    Formats the character rankings as a Markdown table.

    Args:
        encounter_name: The name of the encounter.
        rankings: A list of dictionaries, each representing a player's ranking.

    Returns:
        A string containing the Markdown formatted table.
    """
    if not rankings:
        return "No rankings to display.\n"

    markdown_output = []

    # Title
    markdown_output.append(f"## Top {len(rankings)} DPS Rankings for {encounter_name} (Mythic)\n")

    # Headers
    headers: List[str] = ["Rank", "Player", "DPS", "Class", "Spec", "Guild", "Server", "Report"]
    markdown_output.append(" | ".join(headers))

    # Separator
    markdown_output.append(" | ".join(["---"] * len(headers)))

    # Rows
    for idx, rank_info in enumerate(rankings):
        display_rank = str(rank_info.get('rank', idx + 1)) # Use index + 1 if 'rank' is missing
        guild_name: str = rank_info.get('guild', {}).get('name', 'N/A')
        server_name: str = rank_info.get('server', {}).get('name', 'N/A')
        report_code: str = rank_info.get('report', {}).get('code', 'N/A')

        row_data = [
            display_rank,
            rank_info.get('name', 'N/A'),
            f"{rank_info.get('amount', 0.0):.2f}",
            rank_info.get('class', 'N/A'),
            rank_info.get('spec', 'N/A'),
            guild_name,
            server_name,
            report_code
        ]
        markdown_output.append(" | ".join(map(str, row_data)))

    return "\n".join(markdown_output)

def save_markdown_output(content: str, filename: str = "rankings.md") -> None:
    """
    Saves the given content to a Markdown file.

    Args:
        content: The string content to save.
        filename: The name of the file to save to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Rankings saved to {filename}")
    except IOError as e:
        print(f"Error saving markdown output to file: {e}")

def main() -> None:
    """
    Main function to run the script, orchestrating API calls and display.
    """
    print("Getting access token...")
    access_token: Optional[str] = get_access_token(CLIENT_ID, CLIENT_SECRET)

    if access_token:
        print("Access token received. Fetching rankings...")
        api_response: Optional[Dict[str, Any]] = get_dps_rankings(access_token, ENCOUNTER_ID, DIFFICULTY, METRIC)

        if api_response:
            parsed_data: Optional[Dict[str, Any]] = parse_rankings_response(api_response)
            if parsed_data:
                markdown_table = format_rankings_as_markdown(parsed_data["encounter_name"], parsed_data["rankings"])
                
                save_markdown_output(markdown_table)
            else:
                print("Failed to parse rankings data.")
        else:
            print("Could not retrieve rankings data from the API.")
    else:
        print("Failed to obtain access token. Please check your credentials.")

if __name__ == "__main__":
    main()
# warcraft-logs-api-integration

![Build Status](https://github.com/aluiziolira/warcraft-logs-api-integration/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/aluiziolira/warcraft-logs-api-integration/branch/main/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Overview

This project is a robust Python solution for interacting with the Warcraft Logs GraphQL API. It demonstrates the ability to authenticate, consume, and process complex combat log data, focusing on extracting and presenting performance rankings (DPS) for specific encounters. Ideal for game analysts, community tool developers, or anyone interested in extracting data from GraphQL APIs.

## Technical Highlights & Features

*   **GraphQL API Integration**: Efficient consumption of data from the Warcraft Logs v2 API, using GraphQL queries to fetch detailed ranking information.
*   **Modularity and Best Practices**: Refactored code with cohesive functions, type hinting (`typing`), and docstrings (`Google-style`) for high readability and maintainability.
*   **Secure Credential Management**: Utilization of environment variables (`.env`) to store API keys, ensuring sensitive data is not versioned.
*   **Automation and Code Quality (CI/CD)**: GitHub Actions configuration for linting (`ruff`) and running tests (`pytest`) on every `push` and `pull request`, ensuring code quality and stability.
*   **Data Processing and Presentation**: Logic to parse complex API responses (including nested JSON strings) and format the results into a clean and readable Markdown table, ideal for reports or inclusion in documentation.
*   **Robust Error Handling**: Implementation of `try-except` blocks to handle network failures and JSON parsing errors, providing clear feedback.

## Stack & Tools

*   **Language**: Python 3.9+
*   **Dependency Management**: `pip`
*   **Key Libraries**:
    *   `requests`: For HTTP requests.
    *   `python-dotenv`: For loading environment variables.
    *   `pytest`: Unit testing framework.
    *   `ruff`: High-performance code linter and formatter.
*   **Automation**: GitHub Actions
*   **Version Control**: Git

## Local Setup

To set up and run this project locally on your machine, follow the steps below:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SEU_USUARIO/warcraft-logs-api-integration.git
    cd warcraft-logs-api-integration
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # or
    # .\venv\Scripts\activate  # Windows
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure your Warcraft Logs API credentials**:
    *   Obtain your `client_id` and `client_secret` keys from the Warcraft Logs website.
    *   Create a `.env` file in the project root, copying `credentials.env.example` and filling in your actual keys:
        ```bash
        cp credentials.env.example .env
        # Edit the .env file with your real credentials
        ```

## How to Use / Demonstration

After setup, you can run the main script to fetch and generate the rankings:

```bash
python src/manager/analysis_manager.py
```

This command will:
1.  Authenticate with the Warcraft Logs API.
2.  Fetch the top 10 DPS rankings for the "Gallywix" (Mythic) encounter.
3.  Generate a Markdown formatted table with the results and save it to the `rankings.md` file in the project root.

**Example Output (`rankings.md`):**

```markdown
## Top 10 DPS Rankings for Chrome King Gallywix (Mythic)

| Rank | Player | DPS | Class | Spec | Guild | Server | Report |
|---|---|---|---|---|---|---|---|
| 1 | Tizaxyr | 4929479.14 | Evoker | Devastation | Northern Sky | Blackhand | 84dARJaYzvHMkDPj
| 2 | Livingfour | 4905939.25 | Evoker | Devastation | Exposed | Drak'thul | 1c2qwJbvR4dK8QtL
| 3 | Gilgvoker | 4883182.12 | Evoker | Devastation | poptart corndoG | Tichondrius | P6kVmRJWByHX9GDv
| 4 | Mythvoker | 4831897.58 | Evoker | Devastation | Pescorus | Kazzak | tMQpmzhk1Gwqdj6x
| 5 | Zilsar | 4807295.92 | Hunter | Marksmanship | Wiping As Intended | Draenor | CALV9RDHa1NwQx24
| 6 | Viridia | 4779974.65 | Evoker | Devastation | Liquid | Illidan | G8K6WBjfcwALqmyT
| 7 | Livingtwo | 4748342.89 | Evoker | Devastation | N/A | Drak'thul | 9Pv7L61p4ZMm8VnN
| 8 | Blueprínt | 4726779.22 | Evoker | Devastation | Honestly | Frostmourne | RgPD8fwh6Mvza7mQ
| 9 | 小橘九点睡 | 4705155.24 | Evoker | Devastation | N/A | 血色十字军 | wGTLQPx4h3qYfvat
| 10 | Faxl | 4676745.09 | Evoker | Devastation | Rally | Dalaran | DhfNgZ17b4PpQV6y
```

## Tests

To run the project's unit tests and check code quality:

```bash
pytest
ruff check .
```

## Contribution

Contributions are welcome! Feel free to open issues for suggestions, bug reports, or to submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

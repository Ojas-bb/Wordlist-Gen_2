# Agent Instructions for Wordlist Generator

This project is a command-line wordlist generator written in Python.

## Project Structure

- `wordlist_generator.py`: The main executable script containing all the logic.
- `requirements.txt`: Python dependencies required for the web scraping feature.
- `README.md`: User-facing documentation.
- `test.sh`: A shell script for testing the tool's functionality.

## Development Workflow

1.  **Understand the Goal:** The tool is designed to be a flexible, multi-purpose wordlist creator. It can generate, scrape from URLs, and include existing lists.
2.  **Modify the Script:** All logic is contained within `wordlist_generator.py`. The script uses Python's `argparse` library for command-line parsing.
3.  **Manage Dependencies:** If you add new dependencies, be sure to update the `requirements.txt` file.
4.  **Testing:** Before submitting any changes, you must run the test suite to ensure all features are working correctly. The test script is `test.sh`. You can run it with:
    ```bash
    bash test.sh
    ```
5.  **Update Documentation:** If you add or change any features, update the `README.md` to reflect these changes.

## Testing Procedure

The `test.sh` script is the primary way to verify functionality. It covers:
- Basic word generation (numeric, alpha).
- Output to a file.
- Combining a common list with generation.
- Web scraping (using a local test HTML file).

If you add a new feature, please add a corresponding test case to `test.sh`.

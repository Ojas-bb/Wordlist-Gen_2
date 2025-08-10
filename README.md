# Wordlist Generator

A versatile command-line tool to generate, scrape, and combine wordlists for various purposes, including security auditing.

## Features

- **Generate Wordlists:** Create custom wordlists based on character sets and length.
- **Web Scraping:** Scrape words from any website to create targeted wordlists.
- **Combine Lists:** Prepend your generated list with existing password lists.
- **Flexible Output:** Print to standard output to pipe to other tools, or save directly to a file.

## Installation

1.  Clone the repository or download the `wordlist_generator.py` script.
2.  Install the required Python packages for the web scraping feature:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The script is run from the command line:

```bash
./wordlist_generator.py [OPTIONS]
```

### Options

The tool supports three main modes that can be used alone or in combination: **Generation**, **Web Scraping**, and **Common List Inclusion**.

#### General Options:

-   `-o, --output FILE`: Specify an output file. If omitted, the wordlist is printed to standard output.

#### Generation Options:

These options are used to generate words from scratch. `--min-length` and `--max-length` are required for this mode.

-   `--min-length INT`: The minimum length of words to generate.
-   `--max-length INT`: The maximum length of words to generate.
-   `--charset STRING`: A custom string of characters to use for generation (e.g., "abc123"). This overrides the flags below.
-   `--numeric`: Include numbers `0-9`.
-   `--alpha-lower`: Include lowercase letters `a-z`.
-   `--alpha-upper`: Include uppercase letters `A-Z`.
-   `--special`: Include common special characters `!@#$%^&*`.

#### Web Scraping Options:

-   `--url URL`: The URL of a website to scrape for words. The tool will extract unique alphanumeric words from the page.

#### Common List Options:

-   `--common-list FILE`: Path to a file containing a list of passwords to include at the start of the output.

### Examples

**1. Generate an 8-digit numeric wordlist (e.g., for WPA PIN attacks)**

This command generates all numbers from `00000000` to `99999999` and saves them to `8-digit-pins.txt`.

```bash
./wordlist_generator.py --min-length 8 --max-length 8 --numeric -o 8-digit-pins.txt
```

**2. Generate 4-character lowercase alphabetic words**

```bash
./wordlist_generator.py --min-length 4 --max-length 4 --alpha-lower
```

**3. Scrape all unique words from a website**

This will fetch the content of the URL, extract all unique words, and print them to the terminal.

```bash
./wordlist_generator.py --url http://example.com
```

**4. Combine a common password list with a generated list**

This command first outputs all passwords from `rockyou.txt`, then appends all 3-character words made of `a`, `b`, and `c`.

```bash
./wordlist_generator.py --common-list /path/to/rockyou.txt --min-length 3 --max-length 3 --charset "abc" > combined_list.txt
```

**5. A Note on WPA/WPA2 Passphrases**

WPA/WPA2 passphrases are between 8 and 63 ASCII characters. Brute-forcing this entire space is computationally infeasible. This tool is best used to generate targeted lists based on specific patterns (e.g., 8-10 character passwords with letters and numbers).

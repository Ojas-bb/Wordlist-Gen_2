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
-   `--prefix STRING`: A string to prepend to every word in the output.
-   `--suffix STRING`: A string to append to every word in the output.

#### Generation Options:

The tool offers two mutually exclusive modes for generating words: **Charset Mode** and **Pattern Mode**.

**Charset Mode:**

-   `--min-length INT`: The minimum length of words to generate.
-   `--max-length INT`: The maximum length of words to generate.
-   `--charset STRING`: A custom string of characters to use (e.g., "abc123").
-   `--numeric`: Include numbers `0-9`.
-   `--alpha-lower`: Include lowercase letters `a-z`.
-   `--alpha-upper`: Include uppercase letters `A-Z`.
-   `--special`: Include common special characters `!@#$%^&*`.

**Pattern Mode:**

-   `--pattern STRING`: Generate words from a mask pattern. The following masks are supported:
    -   `?l`: a lowercase letter `a-z`
    -   `?u`: an uppercase letter `A-Z`
    -   `?d`: a digit `0-9`
    -   `?s`: a special character `!@#$%^&*`
    -   `?a`: any of the above characters
    -   `?`: a literal question mark
- Example: `--pattern "pass?d?d?s"` will generate passwords like `pass00!`, `pass01@`, etc.

**Other Generation Options:**

-   `--progress`: Show a progress bar during generation (recommended for large lists).

#### Web Scraping Options:

-   `--url URL`: The URL of a website to scrape for words.
-   `--recursive`: Recursively scrape links found on the initial URL. This will only follow links on the same domain.
-   `--depth INT`: Set the maximum depth for recursion (default: 1). A depth of 1 scrapes the initial page only. A depth of 2 scrapes the initial page and its links.

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

**5. Add a Prefix and Suffix to a Generated List**

This generates 2-character words from 'ab' and adds a prefix of `user_` and a suffix of `_pass`. The output will be `user_aa_pass`, `user_ab_pass`, etc.

```bash
./wordlist_generator.py --min-length 2 --max-length 2 --charset "ab" --prefix "user_" --suffix "_pass"
```

**6. Recursively Scrape a Website to a Depth of 2**

This will scrape the initial page, find all links on it that lead to the same domain, and then scrape those pages as well.

```bash
./wordlist_generator.py --url http://example.com --recursive --depth 2
```

**7. Generate Words from a Pattern**

This will generate words that start with "pw", followed by one uppercase letter and one digit. Output includes `pwA0`, `pwA1`, ..., `pwZ9`.

```bash
./wordlist_generator.py --pattern "pw?u?d"
```

### More Examples

**8. Generate potential usernames**

Create usernames like `chris1990`, `chris1991`... `chris2010`.

```bash
./wordlist_generator.py --pattern "chris?d?d?d?d"
```

**9. Generate 4 to 6 character words with letters and numbers**

```bash
./wordlist_generator.py --min-length 4 --max-length 6 --numeric --alpha-lower
```

**10. Scrape a website and add a prefix**

Useful for creating usernames based on a company's "About Us" page.

```bash
./wordlist_generator.py --url "http://example.com/about" --prefix "ex-"
```

**11. Generate passwords with a literal question mark**

The `?` in a pattern must be escaped with another `?` to be treated as a literal. This generates `pass?1`, `pass?2`, etc.

```bash
./wordlist_generator.py --pattern "pass??d"
```

**12. Pipe output to another tool**

Count how many generated passwords contain the sequence "123".

```bash
./wordlist_generator.py --min-length 5 --max-length 5 --numeric | grep "123" | wc -l
```

**13. Generate complex passwords**

Generate 8-character passwords with the pattern: Uppercase, Lowercase, Lowercase, Lowercase, Digit, Digit, Special, Special.

```bash
./wordlist_generator.py --pattern "?u?l?l?l?d?d?s?s"
```

---
*A Note on WPA/WPA2 Passphrases: WPA/WPA2 passphrases are between 8 and 63 ASCII characters. Brute-forcing this entire space is computationally infeasible. This tool is best used to generate targeted lists based on specific patterns (e.g., 8-10 character passwords with letters and numbers).*

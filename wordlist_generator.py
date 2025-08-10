#!/usr/bin/env python3

import argparse
import string
import itertools
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Generate wordlists based on character sets and length.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Length arguments
    parser.add_argument("--min-length", type=int, help="Minimum length of words for generation.")
    parser.add_argument("--max-length", type=int, help="Maximum length of words for generation.")

    # Character set group
    charset_group = parser.add_argument_group(
        'Character Sets',
        'Define the character set for word generation.\n'
        'Use --charset for a custom set, or combine the flags below.'
    )
    charset_group.add_argument("--charset", type=str, help="A custom string of characters to use (overrides flags).")
    charset_group.add_argument("--numeric", action="store_true", help="Include numeric characters (0-9).")
    charset_group.add_argument("--alpha-lower", action="store_true", help="Include lowercase alphabetic characters (a-z).")
    charset_group.add_argument("--alpha-upper", action="store_true", help="Include uppercase alphabetic characters (A-Z).")
    charset_group.add_argument("--special", action="store_true", help="Include common special characters: !@#$%^&*")

    # Output argument
    parser.add_argument("-o", "--output", type=str, help="Output file path. Defaults to stdout.")

    # New arguments for web scraping and common lists
    source_group = parser.add_argument_group('Word Sources', 'Additional sources for the wordlist.')
    source_group.add_argument("--url", type=str, help="URL of a website to scrape for words.")
    source_group.add_argument("--common-list", type=str, help="Path to a file of common passwords to include.")

    args = parser.parse_args()

    # A generation task requires a character set.
    is_generating = any([args.numeric, args.alpha_lower, args.alpha_upper, args.special, args.charset])

    if is_generating and (args.min_length is None or args.max_length is None):
        parser.error("--min-length and --max-length are required when generating words.")

    if args.min_length and args.max_length and args.min_length > args.max_length:
        parser.error("min-length cannot be greater than max-length.")

    # --- Character set construction for generation ---
    final_charset = ""
    is_generating = any([args.numeric, args.alpha_lower, args.alpha_upper, args.special, args.charset])
    if is_generating:
        if args.charset:
            final_charset = args.charset
        else:
            char_sets = []
            if args.numeric:
                char_sets.append(string.digits)
            if args.alpha_lower:
                char_sets.append(string.ascii_lowercase)
            if args.alpha_upper:
                char_sets.append(string.ascii_uppercase)
            if args.special:
                char_sets.append("!@#$%^&*")
            final_charset = "".join(char_sets)

    # --- Main Logic ---
    output_stream = open(args.output, 'w') if args.output else sys.stdout

    try:
        # 1. Include common password list
        if args.common_list:
            try:
                with open(args.common_list, 'r', errors='ignore') as f:
                    for line in f:
                        output_stream.write(line)
            except FileNotFoundError:
                parser.error(f"Common list file not found: {args.common_list}")
            except Exception as e:
                parser.error(f"Error reading common list file: {e}")

        # 2. Scrape words from URL
        if args.url:
            try:
                import requests
                from bs4 import BeautifulSoup
                import re

                response = requests.get(args.url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text()
                words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower()) # get alphanumeric words, lowercase
                for word in sorted(list(set(words))): # unique, sorted
                    output_stream.write(word + '\n')
            except ImportError:
                 parser.error("Web scraping requires additional packages. Please run: pip install requests beautifulsoup4")
            except requests.exceptions.RequestException as e:
                parser.error(f"Error fetching URL '{args.url}': {e}")
            except Exception as e:
                parser.error(f"An error occurred during web scraping: {e}")

        # 3. Generate words
        if is_generating:
            if not final_charset:
                parser.error("Character set for generation is empty. Use --charset or flags like --numeric.")

            for length in range(args.min_length, args.max_length + 1):
                for item in itertools.product(final_charset, repeat=length):
                    output_stream.write("".join(item) + '\n')

    finally:
        if args.output:
            output_stream.close()


if __name__ == "__main__":
    main()

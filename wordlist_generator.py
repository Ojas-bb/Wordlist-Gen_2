#!/usr/bin/env python3

import argparse
import string
import itertools
import sys
import re
from urllib.parse import urljoin, urlparse

def generate_from_charset(args, output_stream, final_charset):
    """Generates words based on a character set and length range."""
    pbar = None
    if args.progress:
        try:
            from tqdm import tqdm
        except ImportError:
            print("Error: Progress bar requires 'tqdm'. Please run: pip install tqdm", file=sys.stderr)
            sys.exit(1)

        total_words = sum(len(final_charset) ** l for l in range(args.min_length, args.max_length + 1))
        pbar = tqdm(total=total_words, desc="Generating from Charset", unit="word", file=sys.stderr)

    for length in range(args.min_length, args.max_length + 1):
        products = itertools.product(final_charset, repeat=length)
        for item in products:
            word = "".join(item)
            output_stream.write(f"{args.prefix}{word}{args.suffix}\n")
            if pbar:
                pbar.update(1)

    if pbar:
        pbar.close()

def generate_from_pattern(args, output_stream):
    """Generates words from a mask pattern."""
    pattern = args.pattern
    charset_map = {
        'l': string.ascii_lowercase,
        'u': string.ascii_uppercase,
        'd': string.digits,
        's': "!@#$%^&*",
    }
    charset_map['a'] = charset_map['l'] + charset_map['u'] + charset_map['d'] + charset_map['s']

    char_groups = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '?':
            if i + 1 < len(pattern) and pattern[i+1] in charset_map:
                char_groups.append(charset_map[pattern[i+1]])
                i += 2
            else:
                char_groups.append('?')
                i += 1
        else:
            char_groups.append(pattern[i])
            i += 1

    pbar = None
    if args.progress:
        try:
            from tqdm import tqdm
        except ImportError:
            print("Error: Progress bar requires 'tqdm'. Please run: pip install tqdm", file=sys.stderr)
            sys.exit(1)

        total_words = 1
        for group in char_groups:
            total_words *= len(group)
        pbar = tqdm(total=total_words, desc="Generating from Pattern", unit="word", file=sys.stderr)

    products = itertools.product(*char_groups)
    for item in products:
        word = "".join(item)
        output_stream.write(f"{args.prefix}{word}{args.suffix}\n")
        if pbar:
            pbar.update(1)

    if pbar:
        pbar.close()

def main():
    parser = argparse.ArgumentParser(
        description="Generate, scrape, and combine wordlists.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    gen_opts = parser.add_argument_group('General Output Options')
    gen_opts.add_argument("-o", "--output", type=str, help="Output file path. Defaults to stdout.")
    gen_opts.add_argument("--prefix", type=str, default="", help="A string to prepend to each word.")
    gen_opts.add_argument("--suffix", type=str, default="", help="A string to append to each word.")
    gen_opts.add_argument("--progress", action="store_true", help="Show a progress bar during generation.")

    gen_group = parser.add_argument_group('Generation Options', 'Use either charset or pattern mode for generation.')
    gen_group.add_argument("--min-length", type=int, help="[Charset Mode] Minimum length of words.")
    gen_group.add_argument("--max-length", type=int, help="[Charset Mode] Maximum length of words.")
    gen_group.add_argument("--charset", type=str, help="[Charset Mode] A custom string of characters to use.")
    gen_group.add_argument("--numeric", action="store_true", help="[Charset Mode] Include numeric characters (0-9).")
    gen_group.add_argument("--alpha-lower", action="store_true", help="[Charset Mode] Include lowercase letters (a-z).")
    gen_group.add_argument("--alpha-upper", action="store_true", help="[Charset Mode] Include uppercase letters (A-Z).")
    gen_group.add_argument("--special", action="store_true", help="[Charset Mode] Include common special characters.")
    gen_group.add_argument("--pattern", type=str, help="[Pattern Mode] Generate from a mask (e.g., 'pass?d?d').\n"
                                                     "Masks: ?l=lower, ?u=upper, ?d=digit, ?s=special, ?a=all")

    source_group = parser.add_argument_group('Additional Word Sources')
    source_group.add_argument("--url", type=str, help="URL of a website to scrape for words.")
    source_group.add_argument("--recursive", action="store_true", help="Recursively scrape links.")
    source_group.add_argument("--depth", type=int, default=1, help="Maximum depth for recursion.")
    source_group.add_argument("--common-list", type=str, help="Path to a file of common passwords.")

    args = parser.parse_args()

    is_charset_mode = any([args.min_length is not None, args.max_length is not None, args.charset, args.numeric, args.alpha_lower, args.alpha_upper, args.special])

    if args.pattern and is_charset_mode:
        parser.error("Pattern mode (--pattern) cannot be used with charset mode arguments (e.g., --min-length, --numeric).")

    if is_charset_mode and (args.min_length is None or args.max_length is None):
        parser.error("--min-length and --max-length are required when using charset generation mode.")

    if args.min_length and args.max_length and args.min_length > args.max_length:
        parser.error("min-length cannot be greater than max-length.")

    output_stream = open(args.output, 'w') if args.output else sys.stdout

    try:
        if args.common_list:
            try:
                with open(args.common_list, 'r', errors='ignore') as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            output_stream.write(f"{args.prefix}{word}{args.suffix}\n")
            except FileNotFoundError:
                parser.error(f"Common list file not found: {args.common_list}")
            except Exception as e:
                parser.error(f"Error reading common list file: {e}")

        if args.url:
            try:
                import requests
                from bs4 import BeautifulSoup
            except ImportError:
                parser.error("Web scraping requires: pip install requests beautifulsoup4")

            words_to_yield = set()
            visited_urls = set()

            if args.url.startswith('file://'):
                initial_domain = 'local_file'
            else:
                initial_domain = urlparse(args.url).netloc

            def find_words_recursive(url, current_depth):
                if url in visited_urls or (args.recursive and current_depth > args.depth):
                    return
                if not url.startswith('file://') and urlparse(url).netloc != initial_domain:
                    return

                visited_urls.add(url)
                if args.progress:
                    print(f"Scraping: {url} (Depth: {current_depth})", file=sys.stderr)

                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for script in soup(["script", "style"]):
                        script.extract()

                    text = soup.get_text(separator=' ')

                    words_on_page = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
                    words_to_yield.update(words_on_page)

                    if args.recursive and current_depth < args.depth:
                        for link in soup.find_all('a', href=True):
                            absolute_link = urljoin(url, link['href'])
                            find_words_recursive(absolute_link, current_depth + 1)
                except Exception as e:
                    print(f"Warning: Could not process {url}: {e}", file=sys.stderr)

            find_words_recursive(args.url, 1)

            for word in sorted(list(words_to_yield)):
                output_stream.write(f"{args.prefix}{word}{args.suffix}\n")

        if args.pattern:
            generate_from_pattern(args, output_stream)
        elif is_charset_mode:
            final_charset = ""
            if args.charset:
                final_charset = args.charset
            else:
                char_sets = []
                if args.numeric: char_sets.append(string.digits)
                if args.alpha_lower: char_sets.append(string.ascii_lowercase)
                if args.alpha_upper: char_sets.append(string.ascii_uppercase)
                if args.special: char_sets.append("!@#$%^&*")
                final_charset = "".join(char_sets)

            if not final_charset:
                parser.error("Charset generation mode was selected, but no character set was specified.")

            generate_from_charset(args, output_stream, final_charset)

    finally:
        if args.output:
            output_stream.close()

if __name__ == "__main__":
    main()

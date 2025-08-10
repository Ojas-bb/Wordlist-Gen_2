import sys
import re
from urllib.parse import urljoin, urlparse
from gen2_plugins.base import BasePlugin

class UrlSourcePlugin(BasePlugin):
    name = "url_source"
    priority = 11

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('URL Source', 'Options for scraping words from websites.')
        group.add_argument("--url", type=str, help="URL of a website to scrape for words.")
        group.add_argument("--recursive", action="store_true", help="Recursively scrape links.")
        group.add_argument("--depth", type=int, default=1, help="Maximum depth for recursion.")

    def should_run(self):
        return self.args.url is not None

    def run(self):
        """
        Scrapes words from a URL, handling recursion, and yields the sorted, unique results.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("Web scraping requires: pip install requests beautifulsoup4")

        words_to_yield = set()
        visited_urls = set()

        # This needs to handle the case where self.args.url is None, though should_run prevents it.
        if self.args.url.startswith('file://'):
            initial_domain = 'local_file'
        else:
            initial_domain = urlparse(self.args.url).netloc

        def find_words_recursive(url, current_depth):
            if url in visited_urls or (self.args.recursive and current_depth > self.args.depth):
                return
            if not url.startswith('file://') and urlparse(url).netloc != initial_domain:
                return

            visited_urls.add(url)
            if self.args.progress:
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

                if self.args.recursive and current_depth < self.args.depth:
                    for link in soup.find_all('a', href=True):
                        absolute_link = urljoin(url, link['href'])
                        find_words_recursive(absolute_link, current_depth + 1)
            except Exception as e:
                print(f"Warning: Could not process {url}: {e}", file=sys.stderr)

        find_words_recursive(self.args.url, 1)

        for word in sorted(list(words_to_yield)):
            yield word

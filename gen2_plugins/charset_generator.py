import string
import itertools
from gen2_plugins.base import BasePlugin

class CharsetGeneratorPlugin(BasePlugin):
    name = "charset_generator"
    priority = 20

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('Charset Mode', 'For generating via character sets and length')
        group.add_argument("--min-length", type=int, help="Minimum length of words.")
        group.add_argument("--max-length", type=int, help="Maximum length of words.")
        group.add_argument("--charset", type=str, help="A custom string of characters to use.")
        group.add_argument("--numeric", action="store_true", help="Include numeric characters (0-9).")
        group.add_argument("--alpha-lower", action="store_true", help="Include lowercase letters (a-z).")
        group.add_argument("--alpha-upper", action="store_true", help="Include uppercase letters (A-Z).")
        group.add_argument("--special", action="store_true", help="Include common special characters.")

    def should_run(self):
        return any([
            self.args.min_length is not None,
            self.args.max_length is not None,
            self.args.charset,
            self.args.numeric,
            self.args.alpha_lower,
            self.args.alpha_upper,
            self.args.special
        ])

    def run(self):
        """Generates words based on a character set and yields them."""
        import itertools
        import sys

        if self.args.min_length is None or self.args.max_length is None:
            raise ValueError("--min-length and --max-length are required for charset generation.")

        if self.args.min_length > self.args.max_length:
            raise ValueError("min-length cannot be greater than max-length.")

        final_charset = ""
        if self.args.charset:
            final_charset = self.args.charset
        else:
            char_sets = []
            if self.args.numeric: char_sets.append(string.digits)
            if self.args.alpha_lower: char_sets.append(string.ascii_lowercase)
            if self.args.alpha_upper: char_sets.append(string.ascii_uppercase)
            if self.args.special: char_sets.append("!@#$%^&*")
            final_charset = "".join(char_sets)

        if not final_charset:
            raise ValueError("No character set specified for generation.")

        pbar = None
        if self.args.progress:
            try:
                from tqdm import tqdm
            except ImportError:
                raise ImportError("Progress bar requires 'tqdm'. Please run: pip install tqdm")

            total_words = sum(len(final_charset) ** l for l in range(self.args.min_length, self.args.max_length + 1))
            pbar = tqdm(total=total_words, desc="Generating from Charset", unit="word", file=sys.stderr)

        for length in range(self.args.min_length, self.args.max_length + 1):
            products = itertools.product(final_charset, repeat=length)
            for item in products:
                if pbar:
                    pbar.update(1)
                yield "".join(item)

        if pbar:
            pbar.close()

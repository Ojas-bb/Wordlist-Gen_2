import string
import itertools
from gen2_plugins.base import BasePlugin

class PatternGeneratorPlugin(BasePlugin):
    name = "pattern_generator"
    priority = 21

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('Pattern Mode', 'For generating words from a mask pattern.')
        group.add_argument("--pattern", type=str, help="Generate from a mask (e.g., 'pass?d?d').\n"
                                                     "Masks: ?l=lower, ?u=upper, ?d=digit, ?s=special, ?a=all")

    def should_run(self):
        return self.args.pattern is not None

    def run(self):
        """Generates words from a mask pattern and yields them."""
        import sys

        pattern = self.args.pattern
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
        if self.args.progress:
            try:
                from tqdm import tqdm
            except ImportError:
                raise ImportError("Progress bar requires 'tqdm'. Please run: pip install tqdm")

            total_words = 1
            for group in char_groups:
                total_words *= len(group)
            pbar = tqdm(total=total_words, desc="Generating from Pattern", unit="word", file=sys.stderr)

        products = itertools.product(*char_groups)
        for item in products:
            if pbar:
                pbar.update(1)
            yield "".join(item)

        if pbar:
            pbar.close()

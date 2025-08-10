from plugins.base import BasePlugin

class FileSourcePlugin(BasePlugin):
    name = "file_source"
    priority = 10

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('File Source', 'Options for including words from files.')
        group.add_argument("--common-list", type=str, help="Path to a file of common passwords to include.")

    def should_run(self):
        return self.args.common_list is not None

    def run(self):
        """Yields words from the provided file."""
        try:
            with open(self.args.common_list, 'r', errors='ignore') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        yield word
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.args.common_list}")
        except Exception as e:
            raise RuntimeError(f"Error reading file {self.args.common_list}: {e}")

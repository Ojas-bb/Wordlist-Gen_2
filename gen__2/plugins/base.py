class BasePlugin:
    """
    The base class for all wordlist generator plugins.
    """
    # A unique name for the plugin, used for identification.
    name = "base"

    # Execution priority. Lower numbers run first.
    # Recommended priorities:
    # 10-19: Source plugins (reading files, URLs)
    # 20-29: Generator plugins (creating new words)
    # 30-39: Formatter/Mangling plugins (modifying words)
    priority = 100

    def __init__(self, args):
        """
        Initializes the plugin with the parsed command-line arguments.
        """
        self.args = args

    @staticmethod
    def add_arguments(parser):
        """
        Allows the plugin to add its own command-line arguments to the main parser.
        This is a static method, so it's called on the class, not an instance.
        """
        pass

    def should_run(self):
        """
        Determines if the plugin should run based on the provided arguments.
        Returns True if it should run, False otherwise.
        """
        return False

    def run(self, output_stream):
        """
        The main execution method for the plugin. This is where the plugin's
        main logic for generating or processing words should go.
        """
        raise NotImplementedError

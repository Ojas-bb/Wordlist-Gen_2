class BasePlugin:
    """
    The base class for all wordlist generator plugins (gen2 version).
    """
    name = "base"
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
        """
        pass

    def should_run(self):
        """
        Determines if the plugin should run based on the provided arguments.
        """
        return False

    def run(self):
        """
        The main execution method for the plugin. Should be a generator.
        """
        raise NotImplementedError
        yield

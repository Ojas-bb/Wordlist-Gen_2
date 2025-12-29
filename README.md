# Wordlist Generator (Plugin Version)

This wordlist generator features a modular, plugin-based architecture, making it easy to extend with new features.

## Installation

To get started, you need to have Python 3 and `git` installed on your system.

**1. Clone the Repository**

Open your terminal and run the following command to clone the repository into a directory named `wordlist-gen2`.

```bash
git clone https://github.com/Ojas-bb/Wordlist-Gen_2.git
```

After the command finishes, navigate into the new directory:

```bash
cd wordlist-gen2
```

**2. Install Dependencies**

This tool uses a few external Python libraries. Install them using `pip`.

```bash
pip install -r requirements.txt
```

**3. Make the Script Executable**

```bash
chmod +x wordlist_generator.py
```

## Usage

All features are available via command-line arguments. Run with `-h` to see a full list of commands and their options.

```bash
# Example: Generate passwords from a pattern
./wordlist_generator.py --pattern "pw?u?d"
```

---

## Developer Guide: Creating Plugins

This tool is designed to be extensible. You can add your own functionality by creating a new plugin.

### 1. Plugin Location

All plugins are located in the `plugins/` directory. The main script will automatically discover and load any valid plugin file (`.py`) in this directory.

### 2. The BasePlugin Class

Every plugin must inherit from `BasePlugin` (defined in `plugins/base.py`). This class provides the interface for the core engine.

-   `name` (string): A unique name for your plugin.
-   `priority` (integer): Determines execution order (lower runs first).
-   `add_arguments(parser)` (static method): Add your plugin's command-line arguments here.
-   `should_run()` (method): Return `True` if your plugin should execute based on the provided arguments.
-   `run()` (method): A generator that `yield`s words.

### 3. Example: A Simple "Hello" Plugin

```python
# plugins/hello_plugin.py
from plugins.base import BasePlugin

class HelloPlugin(BasePlugin):
    name = "hello"
    priority = 25

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--hello", action="store_true", help="Run the hello plugin.")

    def should_run(self):
        return self.args.hello

    def run(self):
        yield "hello"
        yield "world"
```

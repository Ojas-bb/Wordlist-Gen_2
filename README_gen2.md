# Wordlist Generator (gen2 - Plugin Version)

This is the `gen2` version of the Wordlist Generator, featuring a modular, plugin-based architecture.

## Overview

The functionality of this tool is identical to the `gen-1` version, but the codebase has been refactored to support plugins. This makes it much easier to add new features like new generation methods, new word sources, or new output formatters without modifying the core code.

## Installation

Installation is the same as the `gen-1` version.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Ojas-bb/wordlist---gen1.git wordlist-gen1
    cd wordlist-gen1
    ```

2.  **Install Dependencies**
    ```bash
    # (Optional, but recommended) Create and activate a virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install the required packages
    pip install -r requirements.txt
    ```

3.  **Make the Script Executable**
    ```bash
    chmod +x gen2_wordlist_generator.py
    ```

## Usage

Usage is identical to `gen-1`, just use the `gen2_` script. All command-line arguments are the same.

```bash
./gen2_wordlist_generator.py --pattern "pw?u?d"
```

---

## Developer Guide: Creating Plugins

The `gen2` version is designed to be extensible. You can easily add your own functionality by creating a new plugin.

### 1. Plugin Location

All plugins are located in the `gen2_plugins/` directory. The main script will automatically discover and load any valid plugin file (`.py`) in this directory.

### 2. The BasePlugin Class

Every plugin must be a class that inherits from `BasePlugin`, which is defined in `gen2_plugins/base.py`. The base class provides the interface that the core engine uses to interact with the plugin.

Here are the key methods and attributes you need to implement:

-   `name` (string): A unique, machine-readable name for your plugin (e.g., `"my_generator"`).
-   `priority` (integer): A number that determines the execution order. Lower numbers run first.
    -   `10-19`: Source plugins (e.g., file, URL)
    -   `20-29`: Generator plugins (e.g., charset, pattern)
-   `add_arguments(parser)` (static method): Use this method to add any command-line arguments your plugin needs. Use `parser.add_argument(...)` just as you would with `argparse`.
-   `should_run()` (method): This method should return `True` if your plugin should be executed based on the provided command-line arguments, and `False` otherwise.
-   `run()` (method): This is the main logic of your plugin. It should be a **generator** that `yield`s words one by one.

### 3. Example: A Simple "Hello" Plugin

Here is an example of a simple plugin that adds a `--hello` argument and, if present, outputs the words "hello" and "world".

```python
# gen2_plugins/hello_plugin.py

from .base import BasePlugin

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
By simply creating this file in the `gen2_plugins/` directory, the `gen2` engine will automatically find it, add the `--hello` argument to the help message, and run it when the flag is used.

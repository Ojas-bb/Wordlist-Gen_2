#!/usr/bin/env python3

import argparse
import sys
import os
import importlib
from plugins.base import BasePlugin

def load_plugins():
    """
    Dynamically loads all plugin classes from the 'plugins' directory.
    """
    plugin_classes = []
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")

    # Ensure the plugin directory exists
    if not os.path.isdir(plugin_dir):
        print(f"Warning: Plugin directory '{plugin_dir}' not found.", file=sys.stderr)
        return []

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if isinstance(item, type) and issubclass(item, BasePlugin) and item is not BasePlugin:
                        plugin_classes.append(item)
            except ImportError as e:
                print(f"Warning: Could not import plugin '{module_name}': {e}", file=sys.stderr)

    return plugin_classes

def main():
    parser = argparse.ArgumentParser(
        description="A modular, plugin-based wordlist generator.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Load Plugins and Build Parser ---
    plugin_classes = load_plugins()

    # Add general output options that the core engine will handle
    output_group = parser.add_argument_group('General Output Options')
    output_group.add_argument("-o", "--output", type=str, help="Output file path. Defaults to stdout.")
    output_group.add_argument("--prefix", type=str, default="", help="A string to prepend to each word.")
    output_group.add_argument("--suffix", type=str, default="", help="A string to append to each word.")
    output_group.add_argument("--progress", action="store_true", help="Show progress bars for long operations.")

    # Let each plugin add its own arguments to the parser
    for plugin_class in plugin_classes:
        plugin_class.add_arguments(parser)

    args = parser.parse_args()

    # --- Instantiate and Run Plugins ---

    # Instantiate plugins that should be run
    active_plugins = []
    for plugin_class in plugin_classes:
        plugin_instance = plugin_class(args)
        if plugin_instance.should_run():
            active_plugins.append(plugin_instance)

    # Sort plugins by their priority attribute
    active_plugins.sort(key=lambda p: p.priority)

    if not active_plugins:
        parser.print_help()
        print("\nError: No action specified. Please choose a source or generator.", file=sys.stderr)
        sys.exit(1)

    output_stream = open(args.output, 'w') if args.output else sys.stdout

    try:
        # Keep track of unique words to avoid duplicates from different plugins
        all_words = set()

        for plugin in active_plugins:
            try:
                # The run method should be a generator yielding words
                for word in plugin.run():
                    if word not in all_words:
                        output_stream.write(f"{args.prefix}{word}{args.suffix}\n")
                        all_words.add(word)
            except Exception as e:
                print(f"Error in plugin '{plugin.name}': {e}", file=sys.stderr)
                sys.exit(1)
    finally:
        if args.output:
            output_stream.close()

if __name__ == "__main__":
    main()

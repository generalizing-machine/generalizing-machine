# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
import sys
import json
import click


@click.command()
@click.option('--ANTHROPIC_API_KEY', envvar='ANTHROPIC_API_KEY',
              default='', help='Anthropic API key.')
@click.option('--GITHUB_API_TOKEN', envvar='GITHUB_TOKEN',
              default='', help='GitHub API token for private repo access.')
def main(anthropic_api_key, github_api_token):
    """Generalizing-Machine: an AI agent communicating via stdin/stdout.

    Reads a JSON list of messages from stdin,
    fetches the system prompt from a private GitHub repo,
    calls Anthropic via the electroid package,
    and writes a JSON [text, thoughts] array to stdout.
    """
    # Set environment variables so electroid and githf pick them up
    if anthropic_api_key:
        os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
    if github_api_token:
        os.environ['GITHUB_TOKEN'] = github_api_token

    # Read messages from stdin
    try:
        messages = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(messages, list):
        print("Error: stdin must contain a JSON array of messages.",
              file=sys.stderr)
        sys.exit(1)

    # Run the machine
    from .machine import machine
    text, thoughts = machine(messages)

    # Write the result to stdout as a JSON array
    json.dump([text, thoughts], sys.stdout)


if __name__ == '__main__':
    main()

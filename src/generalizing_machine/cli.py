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
@click.option('--mode', type=click.Choice(['single', 'interactive']),
              default='single',
              help='single: one-shot stdin→stdout. '
                   'interactive: line-delimited JSON loop.')
def main(anthropic_api_key, github_api_token, mode):
    """Generalizing-Machine: an AI agent communicating via stdin/stdout.

    In 'single' mode (default): reads a full JSON array from stdin,
    responds once, and exits.

    In 'interactive' mode: reads one JSON line at a time from stdin,
    responds with one JSON line on stdout, and loops until EOF.
    """
    # Set environment variables so electroid and githf pick them up
    if anthropic_api_key:
        os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
    if github_api_token:
        os.environ['GITHUB_TOKEN'] = github_api_token

    from .machine import machine

    if mode == 'interactive':
        _run_interactive(machine)
    else:
        _run_single(machine)


def _run_single(machine):
    """One-shot mode: read full JSON from stdin, respond, exit."""
    try:
        messages = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(messages, list):
        print("Error: stdin must contain a JSON array of messages.",
              file=sys.stderr)
        sys.exit(1)

    text, thoughts = machine(messages)
    json.dump([text, thoughts], sys.stdout)


def _run_interactive(machine):
    """Interactive mode: line-delimited JSON loop.

    Each line on stdin is a JSON array of messages.
    Each response is a JSON array [text, thoughts] followed by newline.
    Loops until EOF on stdin.
    """
    print("Generalizing-Machine interactive mode ready.", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            messages = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON: {e}", file=sys.stderr)
            continue

        if not isinstance(messages, list):
            print("Error: expected a JSON array of messages.",
                  file=sys.stderr)
            continue

        text, thoughts = machine(messages)
        json.dump([text, thoughts], sys.stdout)
        sys.stdout.write('\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()

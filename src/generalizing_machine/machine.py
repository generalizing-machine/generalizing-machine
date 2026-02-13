# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import os
import sys
import yaml
from . import githf  # from .

# Constants for the private GitHub repo holding the system prompt
MACHINE_ORGANIZATION_NAME = 'generalizing-machine'
PRIVATE_REPO_WITH_TEXT = 'generalizing_machine'
SYSTEM_PROMPT_FILE = 'machina.yaml'


def _fetch_system_prompt():
    """Retrieve the system prompt from a private GitHub repo.
    Falls back to the local machina.yaml if GitHub is unreachable.
    Returns the 'description' field from the YAML as the system prompt string.
    """
    try:
        repo = githf.connect_to_repo(
            organization=MACHINE_ORGANIZATION_NAME,
            repository_name=PRIVATE_REPO_WITH_TEXT,
            private=True
        )
        raw_yaml = githf.read_file(
            repository=repo,
            file_path=SYSTEM_PROMPT_FILE
        )
    except Exception as e:
        print(f"Warning: could not fetch prompt from GitHub: {e}",
              file=sys.stderr)
        local_path = os.path.join(os.path.dirname(__file__), 'machina.yaml')
        with open(local_path, 'r') as f:
            raw_yaml = f.read()

    parsed = yaml.safe_load(raw_yaml)
    return parsed.get('description', 'You are a helpful assistant.')


def machine(messages):
    """Core agent logic.

    1. Fetches the system prompt from a private GitHub repo.
    2. Calls Anthropic via electroid.cloud() with the messages.
    3. Returns (text, thoughts) tuple.
    """
    # Fetch the confidential system prompt
    system_prompt = _fetch_system_prompt()
    # print(f"System prompt loaded ({len(system_prompt)} chars).", file=sys.stderr)

    # Import electroid here (after env vars have been set by cli.py)
    import electroid

    # Call the Anthropic API via electroid
    text, thoughts = electroid.cloud(
        messages=messages,
        system=system_prompt,
        max_tokens=16000
    )

    return text, thoughts


if __name__ == '__main__':
    machine([])

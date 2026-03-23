# iCMD

`iCMD` is a local AI-powered command-line assistant that turns natural language prompts into Linux shell commands, runs the generated command, and prints the result back to your terminal.

## Features

- Converts plain-English requests into bash commands using a local Ollama model
- Executes commands directly from the CLI with a simple `icmd "..."` interface
- Includes basic safety blocking for dangerous commands and shell operators
- Works fully with a local model setup instead of a hosted LLM API

## Usage Examples

```bash
icmd "list all files in this directory"
icmd "print the current working directory"
icmd "show hidden files"
icmd --author
```

Example output:

```bash
$ icmd "print the current working directory"
/home/your_root_directory
```

## Requirements

Before using `iCMD`, make sure the target system has:

- Python 3.8 or newer
- `pip`, `uv`, or `pipx` for installation
- [Ollama](https://ollama.com) installed and running
- The `qwen2.5-coder` model available locally, or network access the first time so Ollama can pull it
- A Linux environment, since the tool generates bash commands

To prepare Ollama manually:

```bash
ollama serve
ollama pull qwen2.5-coder
```

## Installation

### Install from PyPI with uv

For CLI tools, `uv tool install` is the cleanest option:

```bash
uv tool install icmd-cli
```

After installation:

```bash
icmd "list all files"
```

To upgrade later:

```bash
uv tool upgrade icmd-cli
```

### Install with pipx

```bash
pipx install icmd-cli
```

## How It Works

1. You pass a natural-language prompt to `icmd`.
2. The app sends the prompt to Ollama using the `qwen2.5-coder` model.
3. The model returns a bash command.
4. The command is cleaned and checked against a small denylist of dangerous commands and shell symbols.
5. If the command is allowed, `iCMD` executes it and prints the output.

## Safety Notes

`iCMD` includes basic filtering, but it should still be treated as a developer tool and used carefully.

The current safety layer blocks commands involving items such as:

- destructive filesystem tools like `rm` and `mkfs`
- privilege escalation commands like `sudo` and `su`
- remote/network-oriented commands like `curl`, `wget`, `scp`, and `ssh`
- shell operators such as `;`, `|`, `&`, and output redirection

This is a simple safety layer, not a security sandbox.

## CLI Reference

Run a natural-language request:

```bash
icmd "your query"
```

Print the package author:

```bash
icmd --author
```

If no argument is provided, the CLI shows:

```bash
Usage: icmd "your query"
```

## Project Structure

```text
icmd/
├── executor.py
├── llm.py
├── main.py
├── safety.py
└── utils.py
pyproject.toml
README.md
```

## Troubleshooting

### `externally-managed-environment`

Your system Python is managed by the OS. Use a virtual environment, `uv`, or `pipx` instead of installing globally with `pip`.

### `Ollama is not installed or running.`

Install Ollama and make sure the service is available at:

```text
http://localhost:11434
```

### The package installs but `icmd` fails at runtime

Check that:

- Ollama is running
- the `qwen2.5-coder` model exists locally
- the installed package version is the latest one you published

## Author

Built with ❤️ By Deepak Karthick

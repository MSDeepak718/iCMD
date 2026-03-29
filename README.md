# iCMD

`iCMD` is a local AI-powered command-line assistant that turns natural language prompts into Linux shell commands, runs the generated command, and prints the result back to your terminal.

It uses a fine-tuned `Qwen`-based GGUF model hosted on Hugging Face and runs inference locally through a bundled `llama-cli` binary.

## Features

- Converts plain-English requests into bash commands using a fine-tuned local model
- Executes commands directly from the CLI with a simple `icmd "..."` interface
- Downloads the fine-tuned model automatically on first run
- Runs fully locally using a bundled `llama-cli` binary and GGUF weights
- Includes basic safety blocking for dangerous commands and shell operators
- Works without a hosted LLM API after the model is downloaded

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
- a Linux x86_64 environment that can run the bundled `llama-cli` binary
- network access on first run so `iCMD` can download the fine-tuned model from Hugging Face
- A Linux environment, since the tool generates bash commands

## Fine-Tuned Model

`iCMD` uses the fine-tuned model published at:

```text
MSDeepak718/qwen-icmd
```

The downloaded model file is:

```bash
qwen-icmd-q4.gguf
```

On first run, `iCMD` downloads the model to:

```text
~/.icmd_model/qwen-icmd-q4.gguf
```

After that, inference runs locally using the bundled `llama-cli` executable inside the package.

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
2. If needed, the app downloads the fine-tuned GGUF model from Hugging Face.
3. The app runs the prompt locally through the bundled `llama-cli` binary.
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
├── bin/
│   └── llama-cli
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

### The first run takes time

This is expected. `iCMD` downloads the fine-tuned model the first time you use it.

### Model download fails

Make sure you have working network access and that Hugging Face is reachable from your machine.

### `llama-cli` is missing

If `icmd` fails with a missing `icmd/bin/llama-cli` error, the installed package likely does not include the bundled binary. Reinstall or upgrade to the latest published version of `icmd-cli`.

### The package installs but `icmd` fails at runtime

Check that:

```text
~/.icmd_model/qwen-icmd-q4.gguf
```
- the model file exists locally
- the installed package version is the latest one you published
- the installed package includes the bundled `llama-cli` binary

## Author

Built with ❤️ By Deepak Karthick

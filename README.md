# Git Craft

Git Craft is a command line tool that asks an Ollama model to draft a concise commit message from your current Git changes.

## Install

Install with `uv`:

```sh
uv tool install .
```

You can also run it from the project with `uv run git-craft commit-msg`.

## Configure

Git Craft reads `~/.config/gitCraft/config.jsonc` and then applies environment variable overrides. Environment variables take precedence.

```jsonc
{
  // Defaults point to a local Ollama server.
  "base_url": "http://localhost:11434/v1",
  "model_id": "llama3",
  "api_key": ""
}
```

The supported environment variables are `GITCRAFT_BASEURL`, `GITCRAFT_MODELID`, and `GITCRAFT_APIKEY`. The URL should be the OpenAI-compatible API base URL, including `/v1` when required by the server. An API key is optional for a local Ollama instance.

## Use

Stage the changes you want included, then run:

```sh
git-craft commit-msg
```

Pass `--debug` to print the configured model ID, base URL, and API key before the request. The key is printed in full, so use this only in a terminal where its output is safe.

Git Craft uses staged changes when present, otherwise it uses unstaged tracked changes. It prints the generated message without creating a commit. Recent commit subjects are included as context.

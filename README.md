# LLM Editor

A CLI tool to edit files using LLMs.

## Installation

```bash
pip install .
```

## Configuration

Create a directory `~/.llm-editor/` and add a `config.yaml` file:

```yaml
llm:
  provider: openai
  api_key: "your-api-key"
  model: "gpt-4o"

app:
  backup_enabled: true
  backup_suffix: ".backup"
```

## Usage

```bash
edit input.txt
```

Or with options:

```bash
edit input.txt --outfile output.txt
edit input.txt --inplace
```

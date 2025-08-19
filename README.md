# TorahEval

**Provider-agnostic, open-source evaluation infrastructure for Torah knowledge** 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

TorahEval provides standardized, reproducible benchmarking for LLMs on Torah knowledge and understanding. **Works with any model provider** - Groq, OpenAI, Anthropic, Cohere, Google, AWS Bedrock, Azure, local models via Ollama, and more.

## Features

- **🎯 Torah-focused Evaluation**: Comprehensive assessment of Torah knowledge, interpretation, and applications
- **🔧 Simple CLI**: `torahbench list`, `torahbench describe`, `torahbench eval`
- **🏗️ Built on inspect-ai**: Industry-standard evaluation framework
- **🤖 Provider-agnostic**: Works with 15+ model providers out of the box

## 🏃 Speedrun: Evaluate a Model in 60 Seconds

**Prerequisite**: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Create a virtual environment and install TorahEval (30 seconds)
uv venv
source .venv/bin/activate
uv sync

# Set your API key (any provider!)
export GROQ_API_KEY=your_key  # or OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

# Run your first eval (30 seconds)
torahbench eval toraheval --model groq/llama-3.3-70b-versatile --limit 3

# That's it! 🎉 Check results in ./logs/ or view them in an interactive UI:
torahbench view
```

## Using Different Providers

```bash
# Groq (blazing fast!)
torahbench eval toraheval --model groq/meta-llama/llama-4-maverick-17b-128e-instruct

# OpenAI
torahbench eval toraheval --model openai/o3-2025-04-16

# Anthropic
torahbench eval toraheval --model anthropic/claude-sonnet-4-20250514

# Google
torahbench eval toraheval --model google/gemini-2.5-pro

# Local models with Ollama
torahbench eval toraheval --model ollama/llama3.1:70b

# Any provider supported by Inspect AI!
```

## Available Benchmarks

| Category | Benchmarks |
|----------|------------|
| **Torah Knowledge** | TorahEval - comprehensive Torah understanding and interpretation |

## Configuration

```bash
# Set your API keys
export GROQ_API_KEY=your_key
export OPENAI_API_KEY=your_key  # Optional

# Set default model
export BENCH_MODEL=groq/llama-3.1-70b
```

## Commands and Options

For a complete list of all commands and options, run: `torahbench --help`

| Command                  | Description                                   |
|--------------------------|-----------------------------------------------|
| `torahbench`             | Show main menu with available commands        |
| `torahbench list`        | List available evaluations, models, and flags |
| `torahbench eval <benchmark>` | Run benchmark evaluation on a model           |
| `torahbench view`        | View logs from previous benchmark runs        |

### Key `eval` Command Options

| Option               | Environment Variable     | Default                                          | Description                                      |
|----------------------|--------------------------|--------------------------------------------------|--------------------------------------------------|
| `--model`            | `BENCH_MODEL`            | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | Model(s) to evaluate                             |
| `--epochs`           | `BENCH_EPOCHS`           | `1`                                              | Number of epochs to run each evaluation          |
| `--max-connections`  | `BENCH_MAX_CONNECTIONS`  | `10`                                             | Maximum parallel requests to model               |
| `--temperature`      | `BENCH_TEMPERATURE`      | `0.6`                                            | Model temperature                                |
| `--top-p`            | `BENCH_TOP_P`            | `1.0`                                            | Model top-p                                      |
| `--max-tokens`       | `BENCH_MAX_TOKENS`       | `None`                                           | Maximum tokens for model response                |
| `--seed`             | `BENCH_SEED`             | `None`                                           | Seed for deterministic generation                |
| `--limit`            | `BENCH_LIMIT`            | `None`                                           | Limit evaluated samples (number or start,end)    |
| `--logfile`          | `BENCH_OUTPUT`           | `None`                                           | Output file for results                          |
| `--sandbox`          | `BENCH_SANDBOX`          | `None`                                           | Environment to run evaluation (local/docker)     |
| `--timeout`          | `BENCH_TIMEOUT`          | `10000`                                          | Timeout for each API request (seconds)           |
| `--display`          | `BENCH_DISPLAY`          | `None`                                           | Display type (full/conversation/rich/plain/none) |
| `--reasoning-effort` | `BENCH_REASONING_EFFORT` | `None`                                           | Reasoning effort level (low/medium/high)         |

## Building Your Own Evals

TorahEval is built on [Inspect AI](https://inspect.aisi.org.uk/). To create custom evaluations, check out their excellent [documentation](https://inspect.aisi.org.uk/).

## Development

For development work:

```bash
# Clone the repo
git clone https://github.com/SoferAi/toraheval.git
cd toraheval

# Setup with UV
uv venv && uv sync --dev
source .venv/bin/activate

# Run tests
pytest
```

## Contributing

We welcome contributions! Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.



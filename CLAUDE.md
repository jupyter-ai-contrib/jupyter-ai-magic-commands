# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

- A Python library (`jupyter_ai_magic_commands`) that exposes model providers and defines IPython magics
- Uses Python 3.9+ and requires Jupyter ecosystem libraries
- Supports development with both Python and Node.js

## Development Setup

1. Create conda environment:

```bash
conda create -n v3 python=3.13 nodejs=20
conda activate v3
```

2. Development Installation:

```bash
# Install development dependencies
pip install -e ".[dev,all]"
```

## Key Commands

- Install from source: `pip install -e .`
- Development install: `npm run dev:install`
- Uninstall: `npm run dev:uninstall`

## Testing

- Run tests: `pytest`
- Coverage: `pytest --cov`

## Development Dependencies

- Testing: pytest, pytest-asyncio, coverage
- Linting: pre-commit
- Build: hatchling

## Important Notes

- Python version must be >=3.9
- Requires ipython, pydantic (>=2.10.0), click (>=8.1.0)
- Optional integrations include boto3 for Amazon Bedrock

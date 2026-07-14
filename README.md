# INFRASTRUCTURE PROGRAMMABILITY AND AUTOMATION

Lab repository for 06016423 — Infrastructure Programmability and Automation (ITKMITL).

## Requirements

- Python 3.11 (pinned in `.python-version`)
- [uv](https://docs.astral.sh/uv/) — Python package and project manager

Install uv (if you don't have it yet):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repo and sync the environment. `uv sync` creates a virtual environment in `.venv/` and installs all dependencies from `pyproject.toml`:

```bash
git clone https://github.com/Makufff/06016423-IPA.git
cd 06016423-IPA
uv sync
```

## Using the virtual environment

You can either run commands through uv (recommended) or activate the venv manually.

**Option 1 — run through uv (no activation needed):**

```bash
uv run main.py
```

**Option 2 — activate the venv manually:**

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

python main.py

# when done
deactivate
```

## Managing dependencies

```bash
uv add <package>        # add a dependency
uv remove <package>     # remove a dependency
uv sync                 # re-sync the venv with pyproject.toml
```

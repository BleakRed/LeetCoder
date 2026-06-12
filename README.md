# LeetCoder

Automate LeetCode problem fetching, scaffolding, and submission from the command line.

## Features

- **`leetd fetch [N]`** — Fetch any problem by number (or the daily challenge without a number) and scaffold a solution file with boilerplate test runners
- **`leetd show -n N`** — Display problem description, hints, and starter code in the terminal
- **`leetd solve [N]`** — Generate a complete LLM prompt with problem context and starter code
- **`leetd submit <file>`** — Automatically submit a solution to LeetCode via Playwright
- **`leetd list`** — List previously fetched solutions
- **`leetd config`** — View or change configuration

Supported languages: Python, JavaScript, TypeScript, Java, C++, Go, Rust, C#.

## Installation

### Prerequisites

- Python 3.8+
- `pip` (Python package manager)

### Setup

```bash
# Clone the repo (or download leetd.py and leetd)
git clone <repo-url> && cd leetcoder

# (Optional) Install Playwright for the submit feature
pip install playwright
playwright install chromium --with-deps

# Make the CLI accessible
chmod +x leetd
# Optionally symlink or add to PATH:
# ln -s "$PWD/leetd" ~/.local/bin/leetd
```

Cross-platform notes:

| Platform | Shell / PATH tip |
|---|---|
| **Linux** | `ln -s "$PWD/leetd" ~/.local/bin/leetd` (add `~/.local/bin` to `$PATH`) |
| **macOS** | Same as Linux, or use `/usr/local/bin` — `sudo ln -s "$PWD/leetd" /usr/local/bin/leetd` |
| **Windows** | Use `python leetd.py` or create a `.bat` wrapper, or use PowerShell: `New-Alias leetd python.exe path\to\leetd.py` |

## Usage

### Fetch a problem by number

```bash
leetd fetch 1                  # Two Sum → solutions/python/0001_two_sum.py
leetd fetch 175 -l python      # Combine Two Tables (SQL, but gets python snippet if available)
leetd fetch -l cpp             # Daily challenge in C++
leetd fetch 1 -o               # Fetch and open in editor
```

### Show problem info

```bash
leetd show                     # Daily challenge details
leetd show -n 42               # Problem #42 info
leetd show two-sum             # By slug
leetd show -n 1 -l python      # With starter code
```

### Generate an LLM solving prompt

```bash
leetd solve 15 > prompt.md     # Prompt for 3Sum
leetd solve -o prompt.md       # Daily challenge → file
leetd solve 1 -l cpp           # C++ prompt for Two Sum
```

Then pipe `prompt.md` to any LLM.

### Submit a solution

> **Note**: The submit feature is broken due to Cloudflare protections on LeetCode and is unlikely to be fixed.

```bash
leetd submit solutions/python/0001_two_sum.py -u user -p pass
leetd submit solutions/python/0001_two_sum.py --visible   # Watch the browser
leetd submit solutions/python/0001_two_sum.py --save-credentials
```

Credentials can be stored in `~/.config/leetd/config.json`:

```bash
leetd config --set leetcode_username my@email.com
leetd config --set leetcode_password mypass
```

### List saved solutions

```bash
leetd list                     # All languages
leetd list -l python           # Python only
```

### Set default language

```bash
leetd config --set lang cpp
```

## File naming

| Fetch mode | Example filename |
|---|---|
| Daily challenge | `YYYY-MM-DD_problem_title.py` |
| By problem number | `0001_two_sum.py` (4-digit zero-padded) |

Files are saved under `solutions/<language>/`.

## Project structure

```
leetd              # Shell launcher
leetd.py           # Main tool
solutions/         # Fetched solutions (gitignored)
  python/
  cpp/
  javascript/
  ...
```

Manual one-off solutions at the repo root (e.g., `0004_median_of_two_sorted_arrays.py`) are also valid — they aren't managed by `leetd`.

## Submitting (Playwright)

The `submit` command uses Playwright to:
1. Log into LeetCode
2. Navigate to the problem's submission page
3. Paste your code
4. Click Submit

Use `--visible` to watch the browser automation. Pass `--save-credentials` to avoid re-entering login details.

## License

MIT

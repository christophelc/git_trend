# Git Trend

Simple Git activity dashboard showing **net lines of code per week and developer**.

The tool analyzes the Git history of the current repository and generates a `git-dashboard.html` report.

## Requirements

- Git
- Python 3
- Internet access when opening the report (Chart.js is loaded from a CDN)

No Python package installation is required.

## Usage

Run `git_trend.py` from the Git repository you want to analyze.

```bash
cd my_repo

python3 git_trend.py \
  --top-n 3 \
  --from "2026-01"
```

Then open the generated dashboard:

```bash
firefox git-dashboard.html
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `--top-n N` | Number of developers displayed | `10` |
| `--from YYYY-MM` | First month to analyze | 30 days before `--to` |
| `--to YYYY-MM` | Last month to analyze, inclusive | Current date |

## Examples

### Last 30 days

```bash
python3 git_trend.py
```

### Top 3 developers since January 2026

```bash
python3 git_trend.py \
  --top-n 3 \
  --from "2026-01"
```

### March and April 2026

```bash
python3 git_trend.py \
  --from "2026-03" \
  --to "2026-04"
```

### Top 5 developers for 2025

```bash
python3 git_trend.py \
  --top-n 5 \
  --from "2025-01" \
  --to "2025-12"
```

## Metric

For each developer and ISO week:

```text
Net LOC = lines added - lines deleted
```

The dashboard displays **one line per developer on the same chart**.

The Top N developers are selected from their activity over the requested period.

## Output

The command generates:

```text
git-dashboard.html
```

in the current Git repository.

The generated dashboard does not modify the repository.

#!/usr/bin/env python3

import argparse
import calendar
import collections
import json
import subprocess

from datetime import date, timedelta


class Config:
    def __init__(self):
        p = argparse.ArgumentParser()
        p.add_argument("--top-n", type=int, default=10)
        p.add_argument("--from", dest="from_")
        p.add_argument("--to")
        p.add_argument("--text", action="store_true")
        args = p.parse_args()

        self.top_n = args.top_n
        self.text = args.text
        self.end = self.last_day(args.to) if args.to else date.today()
        self.start = self.first_day(args.from_) if args.from_ else self.end - timedelta(days=30)

    @staticmethod
    def first_day(value):
        y, m = map(int, value.split("-"))
        return date(y, m, 1)

    @staticmethod
    def last_day(value):
        y, m = map(int, value.split("-"))
        return date(y, m, calendar.monthrange(y, m)[1])


class GitAnalyzer:
    def __init__(self, config):
        self.config = config
        self.data = collections.defaultdict(lambda: collections.defaultdict(int))

    def analyze(self):
        output = subprocess.check_output([
            "git", "log", "--no-renames",
            f"--since={self.config.start}",
            f"--until={self.config.end + timedelta(days=1)}",
            "--numstat",
            "--format=@@%aN|%ad",
            "--date=format:%G-W%V"
        ], text=True, errors="replace")

        for line in output.splitlines():
            if line.startswith("@@"):
                author, week = line[2:].split("|", 1)
            else:
                fields = line.split("\t")
                if len(fields) >= 2 and fields[0].isdigit() and fields[1].isdigit():
                    self.data[author][week] += int(fields[0]) - int(fields[1])

        return self

    @property
    def branch(self):
        return subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip() or "HEAD"

    @property
    def authors(self):
        return sorted(
            self.data,
            key=lambda a: sum(abs(v) for v in self.data[a].values()),
            reverse=True
        )[:self.config.top_n]

    @property
    def weeks(self):
        return sorted({
            week
            for author in self.authors
            for week in self.data[author]
        })

    def values(self, author):
        return [self.data[author].get(week, 0) for week in self.weeks]


class TextRenderer:
    @staticmethod
    def spark(values):
        bars = "▁▂▃▄▅▆▇█"
        lo, hi = min(values), max(values)

        if lo == hi:
            return bars[0] * len(values)

        return "".join(
            bars[int((v - lo) / (hi - lo) * 7)]
            for v in values
        )

    def render(self, analyzer):
        c = analyzer.config

        print(f"\nGit Trend — {analyzer.branch} — {c.start} → {c.end}")
        print(f"Net LOC / semaine — Top {len(analyzer.authors)}\n")

        print(f'{"Developer":25} {"Trend":<{len(analyzer.weeks)}}  '
              + " ".join(f"{w:>9}" for w in analyzer.weeks))

        for author in analyzer.authors:
            values = analyzer.values(author)
            print(
                f"{author[:25]:25} "
                f"{self.spark(values):<{len(values)}}  "
                + " ".join(f"{v:9}" for v in values)
            )


class HtmlRenderer:
    def render(self, analyzer):
        c = analyzer.config

        series = [{
            "label": author,
            "data": analyzer.values(author)
        } for author in analyzer.authors]

        html = f"""<!doctype html>
<meta charset="utf-8">
<title>Git Trend</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<h2>Net LOC / semaine — {analyzer.branch}</h2>
<p>{c.start} → {c.end} — Top {len(analyzer.authors)} developers</p>

<canvas id="chart"></canvas>

<script>
new Chart(document.getElementById("chart"), {{
  type: "line",
  data: {{
    labels: {json.dumps(analyzer.weeks)},
    datasets: {json.dumps(series)}
  }},
  options: {{
    interaction: {{mode: "index", intersect: false}},
    plugins: {{legend: {{position: "bottom"}}}}
  }}
}});
</script>
"""

        with open("git-dashboard.html", "w") as f:
            f.write(html)

        print("git-dashboard.html")


def main():
    config = Config()
    analyzer = GitAnalyzer(config).analyze()

    renderer = TextRenderer() if config.text else HtmlRenderer()
    renderer.render(analyzer)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import subprocess, collections, json, argparse, calendar
from datetime import date, timedelta

p = argparse.ArgumentParser()
p.add_argument("--top-n", type=int, default=10)
p.add_argument("--from", dest="from_")
p.add_argument("--to")
a = p.parse_args()

def first_day(s):
    y, m = map(int, s.split("-"))
    return date(y, m, 1)

def last_day(s):
    y, m = map(int, s.split("-"))
    return date(y, m, calendar.monthrange(y, m)[1])

end = last_day(a.to) if a.to else date.today()
start = first_day(a.from_) if a.from_ else end - timedelta(days=30)

# add "--all" to commits for all branches: "git", "log", "--all", ...
out = subprocess.check_output([
    "git", "log", "--no-renames",
    f"--since={start}", f"--until={end + timedelta(days=1)}",
    "--numstat", "--format=@@%aN|%ad", "--date=format:%G-W%V"
], text=True, errors="replace")

data = collections.defaultdict(lambda: collections.defaultdict(int))

for line in out.splitlines():
    if line.startswith("@@"):
        author, week = line[2:].split("|", 1)
    else:
        x = line.split("\t")
        if len(x) >= 2 and x[0].isdigit() and x[1].isdigit():
            data[author][week] += int(x[0]) - int(x[1])

# Top N par volume de modifications nettes absolues
top = sorted(data, key=lambda x: sum(abs(v) for v in data[x].values()), reverse=True)[:a.top_n]
weeks = sorted({w for author in top for w in data[author]})

series = [{"label": author,
           "data": [data[author].get(w, 0) for w in weeks]}
          for author in top]

html = f"""<!doctype html>
<meta charset="utf-8">
<title>Git velocity</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<h2>Net LOC / semaine — {start} → {end}</h2>
<canvas id="chart"></canvas>
<script>
new Chart(document.getElementById("chart"), {{
 type:"line",
 data:{{labels:{json.dumps(weeks)},datasets:{json.dumps(series)}}},
 options:{{interaction:{{mode:"index",intersect:false}}}}
}});
</script>"""

open("git-dashboard.html", "w").write(html)
print(f"git-dashboard.html — {len(top)} développeurs — {start} → {end}")

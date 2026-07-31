# VOIS Portfolio Compendium

A tiny static website and structured knowledge base for collecting portfolio references and detecting future VOIS case studies.

## Why this shape

The HTML is disposable. The knowledge is not.

Hermes maintains JSON files that can later feed:

- a personal portfolio site,
- discipline-specific reels,
- case-study pages,
- a résumé evidence bank,
- application-specific selections.

No framework or build step is required.

## Preview locally

Opening `index.html` directly may block JSON loading in some browsers. Run a basic local server instead:

```bash
cd vois-portfolio-compendium
python -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

## Deploy to Vercel

1. Put this folder in a Git repository.
2. Import the repository into Vercel.
3. Framework preset: **Other**.
4. Build command: leave empty.
5. Output directory: `.`

The included `vercel.json` serves the folder as a static site.

## Add a reference

Edit `data/references.json`, or use:

```bash
python scripts/new_reference.py   --title "Music organized by game usage"   --creator "Topfhelm"   --url "https://topfhelm.com/composer"   --disciplines "Music,Game audio"   --summary "Music is grouped by its purpose inside a game."   --takeaway "Context makes the reel easier to evaluate."   --vois-application "Group VOIS cues by exploration, combat, character, interface, and narrative."   --tags "information architecture,game usage"
```

## Scan VOIS Git history

```bash
python scripts/harvest_git_history.py "C:/path/to/vale-of-iseris-LFS"
```

Useful variants:

```bash
python scripts/harvest_git_history.py "C:/path/to/repo" --since "30 days ago"
python scripts/harvest_git_history.py "C:/path/to/repo" --threshold 6
```

The script writes only to:

```text
data/harvested-commits.json
```

Manual candidates remain separate.

## Recommended maintenance loop

- During development: collect screenshots, clips, diagrams, and isolated exports.
- After meaningful commits: run the Git harvester.
- Weekly: promote only the strongest candidates.
- Before building a portfolio: filter by discipline and assemble case studies from the evidence bank.

## Important limitation

The screenshot path supplied in the original request was a local Windows temporary path. It is represented in `data/capture-queue.json`, but the image itself is not included. Copy or upload it before expecting the compendium to display or analyze it.

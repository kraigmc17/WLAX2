# Lola Lacrosse auto-updating PWA

This repository hosts the iPhone PWA and refreshes Lola McConaghy's official Whitman statistics every six hours with GitHub Actions.

## Deploy once
1. Create a new public GitHub repository.
2. Upload every file and folder in this package, preserving the folder structure.
3. In **Settings > Pages**, choose **Deploy from a branch**, branch **main**, folder **/(root)**.
4. In **Settings > Actions > General > Workflow permissions**, select **Read and write permissions**.
5. Open **Actions > Refresh Lola statistics > Run workflow** once.
6. Open the GitHub Pages URL on iPhone Safari, tap **Share**, then **Add to Home Screen**.

## Refresh behavior
- `.github/workflows/update-stats.yml` runs every six hours and can also be run manually.
- `scripts/update_stats.py` retrieves the official Whitman player page, parses accessible statistics tables, validates totals, and writes `data/stats.json`.
- The dashboard requests `data/stats.json` at launch and every 15 minutes while open.
- Completed seasons are retained if the source is temporarily empty.
- GitHub may delay scheduled workflows. A manual run is available from the Actions tab.

## Source configuration
The default player URL is set in `scripts/update_stats.py`. Override it with a GitHub Actions environment variable named `PLAYER_URL` if Whitman changes the roster URL.

## Important maintenance note
Whitman uses a Sidearm-style athletics site. If its table markup changes, the workflow will fail rather than replacing good data with invalid totals. Review the Actions log and adjust the header aliases or parser selectors.

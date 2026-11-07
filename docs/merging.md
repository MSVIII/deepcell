# Combining the forks (Yauren)

Groupmates only fork and build their own version (see `FORKING.md`). Combining the forks into the final game is done here, in the base repository, by Yauren with an AI assistant.

Every fork starts from the tag `fork-base`, and each fork describes its work in `docs/forks/<username>.md`.

## Prompt for the merge

Start a session in a clone of the base repository (https://github.com/Yauren/deepcell) with:

```text
We are combining several forks of Deepcell into the final game. This folder is the base
repository; every fork started from the tag `fork-base`. The forks are:
<list of fork URLs>.

1. Read AGENTS.md, README.md, FORKING.md, docs/merging.md and docs/handoff.md.
2. Add each fork as a git remote and fetch it. For each fork, read its
   docs/forks/<username>.md, then review `git log fork-base..<remote>/master` and
   `git diff fork-base <remote>/master`. Build each fork and note what works.
3. Write docs/merge-plan.md: a table of every feature, balance change, database change
   and asset change across all forks, where forks overlap or conflict, and a proposed
   choice for each (keep, combine, or drop, with the reason). Stop and show me the plan
   before merging anything.
4. After I approve, create a branch `final`, bring the chosen changes in fork by fork
   (merge or cherry-pick, keeping each author's commits), renumber database versions into
   one sequence of non-destructive onUpgrade steps, regenerate assets from tools/ where
   scripts changed, and resolve conflicts in favour of the approved plan.
5. Build, test on an emulator, update every doc in docs/ (design, roadmap, decisions,
   testing, handoff, module-map) and credit each groupmate's features in the README.
```

## Things to watch

- **Database versions**: forks will each have used `DB_VERSION` 4 (and maybe 5). Give every distinct change its own step in one sequence, and make sure a save from the base and a save from each fork both open.
- **Assets**: if two forks changed the same script in `tools/`, combine the scripts first, then regenerate; don't pick exported files by hand.
- **Balance**: `assets/*.json` is where most conflicts will be. Decide the numbers in the merge plan, then play the result.
- **Credits**: list who made what in the README once the final branch builds.

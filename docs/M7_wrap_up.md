# M7: Wrap-up, reproducibility and how everything fits together

**Status:** done. README, findings, report outline, slide plan. Full pipeline verified
reproducible.

## The whole pipeline in one picture
```
configs/*.yaml ──► run.py ──► pd/experiments.py ──► pd/tournament.py ──► pd/game.py ◄── pd/strategies/
                                     │                    │ payoff matrix A
                                     │                    ▼
                                     │               pd/evolution.py (replicator)
                                     ▼
                              results/<EXP>/*.csv  ──► analysis/make_figures.py ──► figures/F*.png|pdf
                                                                   ▲
                                              pd/theory.py (B1–B6) ┘   (also used by tests/)
```

## Reproducibility, verified
- `python run.py all && python analysis/make_figures.py` takes **117 s** on an Apple M3
  (8 cores). The budget is 30 minutes.
- Re-running from scratch reproduced **every file in `results/` byte for byte**, and the
  PDFs are byte-identical too (D36).
- 54 tests pass; `black` and `ruff` are clean.

## Commit history (milestones)
Run `git log --oneline` to see it. Each milestone is one or two commits; the RQ7
predictions commit comes before the E7 results commit.

## What is not done (PRD stretch goals)
Moran process, perception noise, Zero-Determinant extortioner, mutation, dashboard. See
`report/outline.md` → Limitations for how each would extend the results.

## The written report
`report/report.md` is the source. `python report/build_report.py` builds `report.pdf` with
headless Chrome: 15 pages of main text including references, plus 4 pages of appendices.
`node report/build_docx.js` builds `report.docx`, which passes OOXML schema validation.
Figures keep their repository names (Figure F3 = `figures/F3_noise_sweep.png`), so the
report, the slides and the files always match. Every number in the report was checked
against `notes/findings.md` and the result files.

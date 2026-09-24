# 0007. Version control: git and a private GitHub repo
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

## Context
The project folder was not a git repository. The build history should be saved and should tell the story of the build. The GitHub CLI (`gh`) was already logged in as muskii1z.

## Options considered
- **Private GitHub repo.** Backed up off the machine, with full history. Can be flipped to public when portfolio-ready. But nobody can see it yet.
- **Public GitHub repo from day one.** Visible immediately ("building in public"). But early rough work and any accidental mistakes are public.
- **Local git only.** Simplest. But there is no backup, and the master context document says GitHub is the source of truth.

## Decision
Use git plus a private GitHub repo named `rag-motion`, created with the `gh` CLI. Make one small commit per step, so the history tells the build story. Git is initialized in Step 2.

## Tradeoffs
Someone has to remember to make the repo public and tidy the README before sharing it.

## Revisit when
Phase 1 is complete and the README shows the architecture and eval numbers. Then make the repo public.

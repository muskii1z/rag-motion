# 0009. Local database on port 5434, bound to 127.0.0.1
**Date:** 2026-09-24 · **Step:** 3 · **Status:** accepted

## Context
The local Postgres container needs a port on the Mac so the Python code can reach it. Postgres's standard port is 5432. Before choosing, `docker ps -a` showed the developer's other projects also run Postgres in Docker: `jobscout-db-1` on Mac port 5433 (running) and `vh_technology-db-1` on Mac port 5432 (stopped, but configured for it). Two containers cannot use the same Mac port at the same time. A second question was who should be able to connect: only this Mac, or any device on the same network.

## Options considered
- **Mac port 5432.** The standard port, so no one has to remember anything. It was free at the time, but it would collide with `vh_technology` whenever that project was started.
- **Stop or remove the other projects' containers.** Frees up 5432, but those containers belong to other projects. Not ours to touch.
- **Mac port 5434.** No collision with either project. Postgres inside the container still uses 5432; only the Mac side changes.
- **Binding: 0.0.0.0 (all network interfaces, Docker's default) vs 127.0.0.1 (this Mac only).** 0.0.0.0 lets any device on the same network try to connect to the database. 127.0.0.1 limits it to programs on this Mac, which is all we need.

## Decision
Map Mac port 5434 to container port 5432, bound to 127.0.0.1: `"127.0.0.1:5434:5432"` in `docker-compose.yml`. `DATABASE_URL` in `.env.example` is `postgresql://postgres:postgres@localhost:5434/ragmotion`.

## Tradeoffs
A non-standard port has to be remembered. To make that easy, it is written in `.env.example`, in `CLAUDE.md`, and in comments in `docker-compose.yml`. Binding to 127.0.0.1 means another device on the network (for example a laptop) cannot reach this database, which is fine for a solo local setup.

## Revisit when
The app is deployed. A hosted database's connection string replaces this local one entirely, and the port and binding stop mattering. Also revisit if a new local project needs 5434.

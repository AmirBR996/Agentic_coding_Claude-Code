# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run Application**: `uvicorn main:app --reload`
- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Tests**: `pytest`

## Architecture Overview

This is a Python-based web application built with **FastAPI** and **Jinja2** templates.

- **Backend**: `main.py` serves as the entry point, defining routes and managing static files and templates.
- **Frontend**: 
  - HTML templates are located in `/templates` (using Jinja2).
  - Static assets (CSS/JS) are in `/static`.
- **Database**: 
  - The `/database` directory is intended for SQLite integration (defined in `db.py`).
  - Current implementation is in early stages; many routes are placeholders for future steps.

## Project Structure
- `main.py`: FastAPI application and routing.
- `database/`: Database connection and schema management.
- `templates/`: Server-side rendered HTML.
- `static/`: Client-side assets.

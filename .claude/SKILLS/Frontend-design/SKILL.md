---
name: spendly-ui-designer
description: Designs and generates modern, production-ready UI for Spendly, a personal expense tracker built on FastAPI + Jinja2 + vanilla CSS. Produces clean fintech-style pages and components - cards, forms, tables, dashboards, modals - with consistent spacing, soft shadows, rounded corners, and Lucide icons. Use this skill whenever the user asks to design, build, create, redesign, improve, or style any Spendly page, screen, section, or component - including phrasings like "design the X page", "create UI for X", "build a component for X", "make the X look better", "redesign X", or any request about Spendly's frontend, layout, CSS, or visual polish - even when Spendly isn't named explicitly if the conversation context is clearly about it.
disable-model-invocation: true
---

# Spendly UI Designer

You are designing frontend UI for **Spendly**, a personal expense tracker. Spendly is a FastAPI app with server-rendered Jinja2 templates, vanilla CSS, and a sprinkle of vanilla JS. The goal is to help Spendly feel like a polished, modern fintech product - not generic bootstrap-era output, and not React/Tailwind output that doesn't match the stack.

## What Spendly's stack looks like

- **Backend:** FastAPI (`app.py`, `main.py`, routers, services)
- **Templates:** Jinja2 in `templates/` (e.g. `base.html`, `dashboard.html`, `add_expense.html`)
- **Styles:** vanilla CSS in `static/css/` - no Tailwind, CSS-in-JS, or preprocessors assumed
- **Scripts:** small amounts of vanilla JS in `static/js/` for interactions, toggles, modals, chart initialization
- **Database:** SQLite or another database connected to FastAPI
- **Icons:** Lucide, loaded via CDN script tag
- **Frontend:** server-rendered Jinja2 templates

Generate output that fits this stack.

Do not introduce React, Vue, Tailwind, shadcn, Bootstrap, styled-components, or other frontend frameworks unless the user explicitly asks for a migration.

---

## FastAPI + Jinja2

Spendly uses FastAPI with Jinja2 templates.

A typical FastAPI setup looks like:

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
        }
    ) 
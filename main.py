from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database.db import init_db, seed_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html")


@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse(request, "terms.html")


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse(request, "privacy.html")


@app.get("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.get("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.get("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.get("/expenses/{id}/edit")
def edit_expense(id: int):
    return "Edit expense — coming in Step 8"


@app.get("/expenses/{id}/delete")
def delete_expense(id: int):
    return "Delete expense — coming in Step 9"
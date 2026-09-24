from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse , RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
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

# Dependency to protect routes
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        # Redirect to login if not authenticated
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user_id

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html")

@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(request, "register.html", {"request": request, "error": error})

@app.post("/register")
def register_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if not name or not email or not password or not confirm_password:
        return RedirectResponse(url="/register?error=All+fields+are+required", status_code=303)

    if password != confirm_password:
        return RedirectResponse(url="/register?error=Passwords+do+not+match", status_code=303)

    try:
        create_user(name, email, password)
    except Exception: # sqlite3.IntegrityError typically handled here
        return RedirectResponse(url="/register?error=Email+already+registered", status_code=303)

    return RedirectResponse(url="/login?success=Account+created+successfully", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(request, "login.html", {"request": request, "error": error})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        request.session["user_id"] = user["id"]
        return RedirectResponse(url="/profile", status_code=303)

    return RedirectResponse(url="/login?error=Invalid+email+or+password", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, user_id: int = Depends(get_current_user)):
    return HTMLResponse(f"Welcome to your profile, User ID: {user_id}!")

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
def add_expense(user_id: int = Depends(get_current_user)):
    return "Add expense — coming in Step 7"

@app.get("/expenses/{id}/edit")
def edit_expense(id: int, user_id: int = Depends(get_current_user)):
    return "Edit expense — coming in Step 8"

@app.get("/expenses/{id}/delete")
def delete_expense(id: int, user_id: int = Depends(get_current_user)):
    return "Delete expense — coming in Step 9"
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from database.db import init_db, seed_db, get_user_by_email, create_user
from werkzeug.security import check_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="spendly-secret-key")

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
    # Hardcoded data to match reference image
    user_info = {
        "name": "Amir",
        "email": "amir@gmail.com",
        "member_since": "January 2024",
        "initials": "A"
    }
    summary_stats = {
        "total_spent": "₹12,450.75",
        "transaction_count": 8,
        "top_category": "Food"
    }
    transactions = [
        {"date": "12 Apr 2025", "description": "Groceries", "category": "Food", "amount": "₹850.00"},
        {"date": "11 Apr 2025", "description": "Metro card recharge", "category": "Transport", "amount": "₹500.00"},
        {"date": "10 Apr 2025", "description": "Electricity bill", "category": "Bills", "amount": "₹2,200.00"},
        {"date": "09 Apr 2025", "description": "Doctor visit", "category": "Health", "amount": "₹800.00"},
        {"date": "08 Apr 2025", "description": "Netflix subscription", "category": "Entertainment", "amount": "₹649.00"},
        {"date": "07 Apr 2025", "description": "New shoes", "category": "Shopping", "amount": "₹3,200.00"},
        {"date": "05 Apr 2025", "description": "Dinner with friends", "category": "Food", "amount": "₹1,450.00"},
    ]
    category_breakdown = [
        {"category": "Shopping", "amount": "₹3,200.00", "percentage": 25, "color": "var(--color-gold)"},
        {"category": "Other", "amount": "₹2,801.75", "percentage": 22, "color": "var(--color-grey)"},
        {"category": "Food", "amount": "₹2,300.00", "percentage": 18, "color": "var(--color-darkgreen)"},
        {"category": "Bills", "amount": "₹2,200.00", "percentage": 17, "color": "var(--color-blue)"},
        {"category": "Health", "amount": "₹800.00", "percentage": 6, "color": "var(--color-red)"},
        {"category": "Entertainment", "amount": "₹649.00", "percentage": 5, "color": "var(--color-purple)"},
        {"category": "Transport", "amount": "₹500.00", "percentage": 4, "color": "var(--color-purple-light)"},
    ]

    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "request": request,
            "user_info": user_info,
            "summary_stats": summary_stats,
            "transactions": transactions,
            "category_breakdown": category_breakdown
        }
    )

@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse(request, "terms.html")

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse(request, "privacy.html")


@app.get("/expenses/add")
def add_expense(user_id: int = Depends(get_current_user)):
    return "Add expense — coming in Step 7"

@app.get("/expenses/{id}/edit")
def edit_expense(id: int, user_id: int = Depends(get_current_user)):
    return "Edit expense — coming in Step 8"

@app.get("/expenses/{id}/delete")
def delete_expense(id: int, user_id: int = Depends(get_current_user)):
    return "Delete expense — coming in Step 9"
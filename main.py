from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from database.db import (
    init_db, seed_db, get_user_by_email, create_user,
    get_user_by_id, get_expenses_by_user, create_expense,
    get_expense_by_id, update_expense, delete_expense
)
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

# Handle 303 HTTPException as a RedirectResponse
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 303:
        return RedirectResponse(
            url=exc.headers.get("Location", "/login"),
            status_code=303
        )
    # Fallback to a basic response for other HTTPExceptions to avoid crashing
    return HTMLResponse(content=f"HTTP Error {exc.status_code}: {exc.detail}", status_code=exc.status_code)

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request=request, name="landing.html", context={})

@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(request=request, name="register.html", context={"error": error})

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
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})

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
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    expenses = get_expenses_by_user(user_id, start_date, end_date)

    # Calculate summary stats
    total_spent = sum(e["amount"] for e in expenses)
    transaction_count = len(expenses)


    # Find top category
    category_counts = {}
    for e in expenses:
        cat = e["category"]
        category_counts[cat] = category_counts.get(cat, 0) + e["amount"]

    top_category = "None"
    if category_counts:
        top_category = max(category_counts, key=category_counts.get)

    user_info = {
        "name": user["name"],
        "email": user["email"],
        "member_since": user["created_at"][:10], # Simplified date
        "initials": user["name"][0].upper() if user["name"] else "U"
    }

    summary_stats = {
        "total_spent": f"₹{total_spent:,.2f}",
        "transaction_count": transaction_count,
        "top_category": top_category
    }

    transactions = [
        {"id": e["id"], "date": e["date"], "description": e["description"], "category": e["category"], "amount": f"₹{e['amount']:,.2f}"}
        for e in expenses
    ]

    # Category breakdown
    category_colors = {
        "Shopping": "var(--gold)",
        "Food": "var(--darkgreen)",
        "Bills": "var(--blue)",
        "Health": "var(--red)",
        "Entertainment": "var(--purple)",
        "Transport": "var(--purple-light)",
    }

    category_breakdown = []
    for cat, amount in category_counts.items():
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        category_breakdown.append({
            "category": cat,
            "amount": f"₹{amount:,.2f}",
            "percentage": round(percentage),
            "color": category_colors.get(cat, "var(--color-grey)")
        })

    # Sort breakdown by amount descending
    category_breakdown.sort(key=lambda x: float(x["amount"].replace("₹", "").replace(",", "")), reverse=True)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user_info": user_info,
            "summary_stats": summary_stats,
            "transactions": transactions,
            "category_breakdown": category_breakdown,
            "start_date": start_date,
            "end_date": end_date
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
def analytics(request: Request, user_id: int = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="analytics.html", context={})

@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html", context={})

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html", context={})


from datetime import date

@app.get("/expenses/add", response_class=HTMLResponse)
def add_expense(request: Request, user_id: int = Depends(get_current_user)):
    error = request.query_params.get("error")
    today = date.today().isoformat()
    return templates.TemplateResponse(
        request=request,
        name="add_expense.html",
        context={"error": error, "today_date": today}
    )

@app.post("/expenses/add")
def add_expense_post(
    request: Request,
    user_id: int = Depends(get_current_user),
    amount: float = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    description: str = Form(None)
):
    if amount <= 0:
        return RedirectResponse(url="/expenses/add?error=Amount+must+be+greater+than+zero", status_code=303)

    if not category or not date:
        return RedirectResponse(url="/expenses/add?error=Category+and+date+are+required", status_code=303)

    try:
        create_expense(user_id, amount, category, date, description)
    except Exception as e:
        return RedirectResponse(url=f"/expenses/add?error=Database+error:+{str(e)}", status_code=303)

    return RedirectResponse(url="/profile", status_code=303)

@app.get("/expenses/{id}/edit", response_class=HTMLResponse)
def edit_expense(id: int, request: Request, user_id: int = Depends(get_current_user)):
    expense = get_expense_by_id(id, user_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="edit_expense.html",
        context={"expense": expense, "error": error}
    )

@app.post("/expenses/{id}/edit")
def edit_expense_post(
    id: int,
    request: Request,
    user_id: int = Depends(get_current_user),
    amount: float = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    description: str = Form(None)
):
    # Re-verify ownership before updating
    expense = get_expense_by_id(id, user_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if amount <= 0:
        return RedirectResponse(url=f"/expenses/{id}/edit?error=Amount+must+be+greater+than+zero", status_code=303)

    if not category or not date:
        return RedirectResponse(url=f"/expenses/{id}/edit?error=Category+and+date+are+required", status_code=303)

    try:
        update_expense(id, user_id, amount, category, date, description)
    except Exception as e:
        return RedirectResponse(url=f"/expenses/{id}/edit?error=Database+error:+{str(e)}", status_code=303)

    return RedirectResponse(url="/profile", status_code=303)

@app.get("/expenses/{id}/delete")
def delete_expense_route(id: int, user_id: int = Depends(get_current_user)):
    delete_expense(id, user_id)
    return RedirectResponse(url="/profile", status_code=303)
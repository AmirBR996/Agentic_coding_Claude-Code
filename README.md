# Spendly: Smart Expense Tracking, Agentically Crafted

Spendly is a lightweight, intuitive expense tracker designed to help users manage their daily spending with ease. While it provides a seamless financial management experience, its primary purpose is to serve as a living showcase for **Agentic Coding** using Claude Code.

## 🤖 The Agentic Coding Showcase

Spendly was not written through traditional manual coding. Instead, it was *steered* by a human using Claude Code, demonstrating a modern AI-driven Software Development Lifecycle (SDLC).

### The Spec-Driven Workflow
The project follows a rigorous **Spec $\rightarrow$ Implement $\rightarrow$ Verify** loop, ensuring that every feature is intentionally designed before a single line of code is written:

1. **Specification (`.claude/specs/`)**: Every feature begins as a detailed markdown specification. These specs define the "What" (requirements) and the "How" (architectural approach), providing a source of truth for the agent.
2. **Implementation**: Claude Code executes the specification, creating dedicated feature branches and implementing the logic across the backend and frontend.
3. **Verification (`/test_feature`)**: Once implemented, a specialized agent generates and runs `pytest` suites based on the original specification—not the code—to ensure the feature behaves exactly as intended.

### The Agentic Brain
The `.claude/` directory acts as the "brain" of the project, containing:
- **Custom Agents**: Specialized personas for quality review, security auditing, and test generation.
- **Custom Commands**: Specialized tools for tasks like seeding realistic dummy data (`/seed_user`, `/seed_expense`) and initiating new feature specs.

This approach ensures complete traceability, reduces regressions, and transforms the role of the developer from a "writer of code" to an "architect of intent."

---

## 🛠 Technical Architecture

Spendly is built on a modern, high-performance Python stack:

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) - Handling routing, session management, and business logic.
- **Frontend**: [Jinja2](https://jinja.palletsprojects.com/) - Server-side rendered HTML templates for a fast, responsive UI.
- **Database**: [SQLite](https://www.sqlite.org/) - A lightweight, file-based data store for user profiles and transactions.

### Project Structure Map
```text
├── .claude/            # The Agentic Brain (Specs, Agent Definitions, Commands)
│   └── specs/          # Feature specifications (The blueprint of the app)
├── database/           # Data Access Layer (DAL)
│   └── db.py           # SQLite connection and CRUD operations
├── static/             # Client-side assets (CSS, JS)
├── templates/          # Jinja2 HTML Views
├── tests/              # Feature-specific pytest suites
├── main.py             # Central Controller (FastAPI routes & app entry)
└── spendly.db          # SQLite database file
```

---

## ✨ Features

- **Secure Authentication**: User registration and login with hashed passwords.
- **Expense Management**: Full CRUD capabilities to track spending by amount, category, and date.
- **Personal Dashboard**: A comprehensive profile view featuring:
  - Total spending summaries.
  - Top spending category identification.
  - Date-filtered transaction history.
  - Visual category breakdowns.
- **Developer Utilities**: Automated database seeding for rapid prototyping and testing.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A virtual environment (recommended)

### Installation
```bash
# Install required dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the FastAPI server with auto-reload
uvicorn main:app --reload
```
The app will be available at `http://127.0.0.1:8000`.

### Running Tests
```bash
# Execute the feature-specific test suite
pytest
```

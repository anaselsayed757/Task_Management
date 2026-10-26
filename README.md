# Task Management System (Flask)

## Overview

This is a full-stack task management web application built with:
- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite for storage
- Jinja2 templates plus static JS/CSS for UI

Features:
- User register/login/logout
- Dashboard with user-specific tasks
- Task CRUD via API (`/api/tasks`)
- Task assignment, priority, status, deadlines
- Demo data seeder script

---

## Files and structure

- `app.py`: main Flask app and routes
- `models.py`: SQLAlchemy models `User` and `Task`
- `templates/`: HTML views (`index`, `register`, `login`, `dashboard`)
- `static/js/app.js`: client-side task management and API calls
- `static/css/style.css`: styles
- `requirements.txt`: dependencies
- `start.sh`: virtualenv activation + `python app.py`
- `seed_demo_data.py`: populate `taskmanager.db` with sample users/tasks

---

## Setup (from scratch)

1. Clone repository:
   ```bash
   git clone <repo-url>
   cd task-management-system
   ```

2. Create/activate virtualenv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start app:
   ```bash
   ./start.sh
   # or
   python app.py
   ```

5. Open browser:
   - `http://127.0.0.1:5000`

---

## Seed demo data

```bash
python seed_demo_data.py
```

Login credentials added by seed script (example):
- `john_doe` / `password123`
- `sarah_smith` / `password123`
- `mike_wilson` / `password123`
- `emily_brown` / `password123`

---

## Behavior

- At startup, `app.py` runs `db.create_all()` using `sqlite:///taskmanager.db`.
- `/register` validates unique username/email and stores hashed password.
- `/login` authenticates via `Flask-Login`.
- `/dashboard` shows tasks owned or assigned to logged-in user.
- API endpoints require login and return JSON:
  - `GET /api/tasks`
  - `POST /api/tasks`
  - `GET|PUT|DELETE /api/tasks/<id>`

---

## Quick troubleshooting

- If you get missing package errors:
  ```bash
  pip install -r requirements.txt
  ```
- If port 5000 is busy:
  ```bash
  flask run --port 5001
  ```
- Reset database:
  ```bash
  rm -f taskmanager.db
  python app.py
  ```

---

## Next improvements

- Add Flask-Migrate for DB migrations
- Store secret key in environment
- Add validation and RBAC
- Add tests with `pytest`

---

## Run checklist

- [x] Virtualenv created
- [x] Dependencies installed
- [x] App started
- [x] Browser login works
- [x] Tasks CRUD works

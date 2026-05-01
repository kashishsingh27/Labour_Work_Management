<div align="center">

# ⚒️ LWMS
### Labour Work Management System

**A full-stack web platform connecting contractors and skilled labour workers across India.**

![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

🌐 **Live Demo:** [labour-work-management.onrender.com](https://labour-work-management.onrender.com)

</div>

---

## 📌 What is LWMS?

LWMS is a web-based workforce management platform built with **Flask** that bridges the gap between **contractors** who need skilled labour and **workers** who need jobs. It handles everything from job posting and applications to email notifications, ratings, and dashboards — all in one place.

> Built for India's construction and daily wage workforce. Simple, fast, and mobile-friendly.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🏗️ **Job Posting** | Contractors post jobs with title, location, wage, and work type |
| 📬 **Instant Notifications** | Labour workers in the same city get notified via email + in-app bell |
| ✅ **Application Management** | Accept or reject applicants with one click |
| ⭐ **Ratings & Reviews** | Contractors rate workers after job completion |
| 🔍 **Smart Job Filtering** | Filter by city, pincode, minimum wage, work type |
| 📊 **Role Dashboards** | Separate dashboards with charts and stats for each role |
| 🌙 **Dark / Light Mode** | Persistent theme toggle across all pages |
| 🔒 **Secure Auth** | Hashed passwords, role-based access control, login-required guards |
| 📋 **Structured Logging** | Every key action logged — logins, job creation, email failures, duplicates |
| 🛡️ **Graceful Error Handling** | Try/except on all critical paths — app never crashes on email failure |

---

## 🧱 Tech Stack

```
Backend      →  Flask (Python 3.14)
Database     →  SQLAlchemy ORM + SQLite (dev) / PostgreSQL (prod-ready)
Migrations   →  Flask-Migrate (Alembic)
Frontend     →  Jinja2 + Bootstrap 5.3 + Chart.js
Auth         →  Flask-Login + Bcrypt
Email        →  Flask-Mail (Gmail SMTP)
Logging      →  Python logging module (Render-compatible format)
Deployment   →  Render (free tier)
```

---

## 👥 User Roles

### 🏢 Contractor
- Register with name, city, email, phone
- Post jobs with location, wage, work type, description
- View and manage all applications grouped by job
- Accept or reject workers (labour gets email + in-app notification)
- Rate and review workers after job completion
- Delete jobs with full cascade cleanup
- View own profile with stats and charts

### 👷 Labour Worker
- Register with city and contact info
- Browse and filter jobs by city, pincode, wage, work type
- Apply to jobs with one click (duplicate prevention built in)
- Track application status — Pending / Accepted / Rejected
- Receive email + in-app notifications for new jobs in their city
- View ratings and build reputation over time

---

## 🔐 Authentication & Authorization

Every route is protected at two levels:

**Level 1 — Login required:**
```python
@login_required  # redirects to login if not authenticated
```

**Level 2 — Role verification:**
```python
if current_user.role != "contractor":
    flash("Access denied.", "danger")
    return redirect(url_for("auth.login"))
```

This ensures a labour user can never access contractor routes and vice versa — even if they manually type the URL.

---

## 🛡️ Error Handling & Logging

All database operations and email sends are wrapped in try/except blocks so the app never crashes on external failures:

```python
# Job creation — safe with rollback on failure
try:
    db.session.add(job)
    db.session.commit()
except Exception:
    db.session.rollback()
    flash("Error creating job. Please try again.", "danger")

# Email — fails silently, never blocks the request
try:
    mail.send(msg)
except Exception as e:
    logging.warning(f"Email failed for {labour.email}: {str(e)}")
```

**Logging format (Render-compatible):**
```
2026-05-01 01:33:11 | INFO  | User 3 attempting to post a job
2026-05-01 01:33:11 | INFO  | Job 'Plumbing work' created by user 3
2026-05-01 01:33:11 | WARNI | Email failed for user@example.com: [reason]
2026-05-01 01:33:11 | WARNI | Duplicate application attempt: user 2, job 1
2026-05-01 01:33:11 | WARNI | Failed login attempt: user@example.com
```

---

## 📬 Email Notification Flow

```
Contractor posts job
        │
        ▼
Query all labour users in same city
        │
        ▼
For each labour:
  ├── In-app Notification created in DB  ✅ always works
  └── Email sent via Flask-Mail          ⚠️ gracefully skipped if SMTP fails
        │
        ▼
Labour dashboard shows unread count badge on bell icon
```

When application is accepted:
```
Contractor clicks Accept
        │
        ▼
Application.status → "Accepted" in DB
        │
        ▼
In-app Notification created  +  Email sent with job + contractor contact details
```

> **Note:** On the live Render deployment, SMTP is suppressed via `MAIL_SUPPRESS_SEND=true`
> because Render's free tier blocks outbound SMTP connections. Email works fully on localhost.

---

## 🗂️ Project Structure

```
LWMS/
├── app/
│   ├── auth/
│   │   └── routes.py          # Login, register, logout, notifications, setup-db
│   ├── contractor/
│   │   └── routes.py          # Job posting, applications, rating, profile
│   ├── labour/
│   │   └── routes.py          # Job browsing, applying, dashboard, profile
│   ├── templates/
│   │   ├── base.html          # Navbar, flash messages, theme toggle
│   │   ├── index.html         # Landing page with live job preview
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── notifications.html
│   │   ├── contractor/
│   │   │   ├── dashboard.html
│   │   │   ├── post_job.html
│   │   │   ├── applications.html
│   │   │   ├── rate_labour.html
│   │   │   └── contractor_profile.html
│   │   └── labour/
│   │       ├── dashboard.html
│   │       ├── jobs.html
│   │       ├── job_details.html
│   │       ├── single_job.html
│   │       └── labour_profile.html
│   ├── static/
│   ├── models.py              # User, Job, Application, Notification, Rating
│   ├── extensions.py          # db, bcrypt, login_manager, mail, migrate
│   └── __init__.py            # App factory — create_app()
├── migrations/                # Alembic migration files
├── config.py                  # All config including mail, db, secret key
├── instance/
│   └── site.db                # SQLite DB (local only)
└── requirements.txt
```

---

## 🗄️ Database Models

```python
User          →  id, username, email, password, role, city, phone, created_at
Job           →  id, title, description, city, locality, landmark, pincode,
                 wage, work_type, contractor_id, created_at
Application   →  id, labour_id, job_id, status, created_at
Notification  →  id, user_id, message, job_id, is_read, created_at
Rating        →  id, labour_id, contractor_id, job_id, rating, review, created_at
```

**Application status flow:**
```
Pending  →  Accepted
         →  Rejected
```

---

## 🚀 Getting Started (Local)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/lwms.git
cd lwms
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file:
```env
SECRET_KEY=your-secret-key

MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password

# Leave these unset locally — defaults will be used
# MAIL_SUPPRESS_SEND=false   (default, emails send normally on localhost)
# DATABASE_URL=               (default, uses SQLite locally)
```

> **Gmail setup:** You need a Gmail **App Password**, not your regular password.
> Go to Google Account → Security → 2-Step Verification → App Passwords.

### 5. Initialize the database
```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 6. Run the app
```bash
flask run
```

Open `http://127.0.0.1:5000` in your browser.

---

## ☁️ Deployment (Render)

The app is deployed on [Render](https://render.com) free tier.

### Environment variables to set on Render:

| Key | Value |
|---|---|
| `SECRET_KEY` | your secret key |
| `MAIL_USERNAME` | your Gmail address |
| `MAIL_PASSWORD` | your Gmail app password |
| `MAIL_SUPPRESS_SEND` | `true` |

> `MAIL_SUPPRESS_SEND=true` is required on Render because the free tier blocks
> outbound SMTP connections. This keeps the app stable while preserving all
> email logic for local demonstration.

### Database on Render
The app currently uses SQLite on Render. Since Render's free tier has an **ephemeral filesystem**, the database is wiped on every redeploy. After each redeploy:

1. Visit `/setup-db` to recreate tables
2. Re-register your accounts

For persistent storage, set `DATABASE_URL` to a PostgreSQL connection string — the app will switch automatically since `SQLALCHEMY_DATABASE_URI` reads from that env var.

---

## 📡 Route Overview

| Blueprint | Route | Method | Description |
|---|---|---|---|
| `auth` | `/` | GET | Home / Landing page |
| `auth` | `/register` | GET, POST | User registration |
| `auth` | `/login` | GET, POST | User login |
| `auth` | `/logout` | GET | Logout |
| `auth` | `/notifications` | GET | View in-app notifications |
| `auth` | `/setup-db` | GET | Run migrations (Render utility route) |
| `contractor` | `/contractor/dashboard` | GET | Contractor dashboard |
| `contractor` | `/contractor/post-job` | GET, POST | Post a new job |
| `contractor` | `/contractor/applications` | GET | View all applications |
| `contractor` | `/contractor/application/<id>/accept` | GET | Accept application |
| `contractor` | `/contractor/application/<id>/reject` | GET | Reject application |
| `contractor` | `/contractor/job/<id>/delete` | POST | Delete job + cascade |
| `contractor` | `/contractor/rate/<job_id>/<labour_id>` | GET, POST | Rate a worker |
| `contractor` | `/contractor/profile/<id>` | GET | Contractor profile |
| `contractor` | `/contractor/profile/<id>/edit` | POST | Edit contractor profile |
| `labour` | `/labour/dashboard` | GET | Labour dashboard |
| `labour` | `/labour/jobs` | GET | Browse and filter jobs |
| `labour` | `/labour/apply/<job_id>` | GET | Apply to job |
| `labour` | `/labour/job/<id>` | GET | Job detail view |

---

## 🎨 Frontend Design System

The UI is built on a custom design system layered on top of Bootstrap 5.

**Fonts:** `Poppins` (headings, buttons) + `Inter` (body text)

**Theme:** Full dark/light mode via CSS variables, persisted in `localStorage`

**Color palette:**
```
Accent blue    →  #2563eb
Accent light   →  #eff6ff
Success green  →  #16a34a
Warning amber  →  #d97706
Danger red     →  #dc2626
```

**Key components:** Stat cards, status pills, notification badges,
avatar initials, animated blobs (auth pages), Chart.js dashboards

---

## ⚠️ Known Limitations

| Limitation | Details |
|---|---|
| SQLite on Render | DB wiped on every redeploy — switch to PostgreSQL via `DATABASE_URL` for persistence |
| SMTP blocked on Render | Free tier blocks outbound SMTP — use `MAIL_SUPPRESS_SEND=true`, email works on localhost |
| No real-time updates | Notifications require page refresh — WebSockets planned for future |

---

## 🗺️ Roadmap

- [x] User registration and login (contractor + labour)
- [x] Role-based access control on every route
- [x] Job posting with location details
- [x] Application system (apply, accept, reject)
- [x] Duplicate application prevention
- [x] Email + in-app notifications
- [x] Graceful email failure handling (try/except on all mail calls)
- [x] Structured logging across all routes
- [x] Ratings and reviews
- [x] Role-specific dashboards with Chart.js
- [x] Dark / light mode
- [x] Delete job with cascade cleanup (applications, notifications, ratings)
- [x] Flask-Migrate for database migrations
- [x] Render deployment with environment-based config
- [ ] PostgreSQL for persistent production storage
- [ ] Job expiry / auto-close (`is_active` + `expires_at`)
- [ ] `Completed` application status tied to job closure
- [ ] Profile photo upload
- [ ] Radius-based job matching
- [ ] Real-time push notifications (WebSockets)
- [ ] HTTP-based email service (Resend/SendGrid) for production
- [ ] Mobile app (React Native)
- [ ] AI-based worker matching

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ using Flask &nbsp;·&nbsp; Bootstrap 5 &nbsp;·&nbsp; SQLAlchemy &nbsp;·&nbsp; Deployed on Render

</div>
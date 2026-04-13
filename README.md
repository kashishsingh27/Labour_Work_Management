<div align="center">

# ⚒️ LWMS
### Labour Work Management System

**A full-stack web platform connecting contractors and skilled labour workers across India.**

![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## 📌 What is LWMS?

LWMS is a web-based workforce management platform built with **Flask** that bridges the gap between **contractors** who need skilled labour and **workers** who need jobs. It handles everything from job posting and applications to email notifications, ratings, and dashboards — all in one place.

> Built for India's construction and daily wage workforce. Simple, fast, and mobile-friendly.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🏗️ **Job Posting** | Contractors post jobs with title, location, wage, work type |
| 📬 **Instant Notifications** | Labour workers in the same city get notified by email + in-app |
| ✅ **Application Management** | Accept or reject applicants with one click |
| ⭐ **Ratings & Reviews** | Contractors rate workers after job completion |
| 🔍 **Smart Job Filtering** | Filter by city, pincode, wage, work type |
| 📊 **Dashboards** | Role-specific dashboards with charts and stats |
| 🌙 **Dark / Light Mode** | Persistent theme toggle across all pages |
| 🔒 **Secure Auth** | Hashed passwords, role-based access control |

---

## 🧱 Tech Stack

```
Backend      →  Flask (Python)
Database     →  SQLAlchemy ORM + SQLite
Frontend     →  Jinja2 + Bootstrap 5.3 + Chart.js
Auth         →  Flask-Login + Bcrypt
Email        →  Flask-Mail
```

---

## 👥 User Roles

### 🏢 Contractor
- Post jobs with location, wage, work type, description
- View and manage all applications grouped by job
- Accept or reject workers (they get notified by email)
- Rate workers after job completion
- Delete jobs when no longer needed

### 👷 Labour Worker
- Browse and filter jobs by city, pincode, wage, work type
- Apply to jobs with one click
- Track application status (Pending / Accepted / Rejected)
- Receive email + in-app notifications for new jobs in their city
- View ratings and build reputation

---

## 🗂️ Project Structure

```
LWMS/
├── app/
│   ├── auth/
│   │   └── routes.py          # Login, register, notifications, profiles
│   ├── contractor/
│   │   └── routes.py          # Job posting, applications, rating
│   ├── labour/
│   │   └── routes.py          # Job browsing, applying, dashboard
│   ├── templates/
│   │   ├── base.html          # Navbar, flash messages, theme toggle
│   │   ├── index.html         # Landing page
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
│   ├── extensions.py          # db, bcrypt, login_manager, mail
│   └── __init__.py
├── instance/
│   └── site.db
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
Pending  →  Accepted  →  (Completed — planned)
         →  Rejected
```

---

## 🚀 Getting Started

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
Create a `.env` file or set these in your Flask config:
```env
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

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

## 📡 Route Overview

| Blueprint | Route | Method | Description |
|---|---|---|---|
| `auth` | `/` | GET | Home / Landing page |
| `auth` | `/register` | GET, POST | User registration |
| `auth` | `/login` | GET, POST | User login |
| `auth` | `/logout` | GET | Logout |
| `auth` | `/notifications` | GET | View notifications |
| `auth` | `/profile/labour/<id>` | GET | Labour profile |
| `auth` | `/profile/contractor/<id>` | GET | Contractor profile |
| `contractor` | `/contractor/dashboard` | GET | Contractor dashboard |
| `contractor` | `/contractor/post-job` | GET, POST | Post a new job |
| `contractor` | `/contractor/applications` | GET | View all applications |
| `contractor` | `/contractor/application/<id>/accept` | GET | Accept application |
| `contractor` | `/contractor/application/<id>/reject` | GET | Reject application |
| `contractor` | `/contractor/job/<id>/delete` | POST | Delete a job |
| `contractor` | `/contractor/rate/<job_id>/<labour_id>` | GET, POST | Rate a worker |
| `labour` | `/labour/dashboard` | GET | Labour dashboard |
| `labour` | `/labour/jobs` | GET | Browse jobs |
| `labour` | `/labour/apply/<job_id>` | GET | Apply to job |
| `labour` | `/labour/job/<id>` | GET | Job detail |

---

## 📬 Email Notification Flow

```
Contractor posts job
        │
        ▼
All labour users in same city
        │
        ▼
Email sent via Flask-Mail  +  In-app Notification created
        │
        ▼
Labour dashboard shows unread count badge on bell icon
```

When application is accepted or rejected:
```
Contractor clicks Accept / Reject
        │
        ▼
Application.status updated in DB
        │
        ▼
Notification created for labour  +  Email sent with job + contractor details
```

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

## 🗺️ Roadmap

- [x] User registration and login (contractor + labour)
- [x] Job posting with location details
- [x] Application system (apply, accept, reject)
- [x] Email + in-app notifications
- [x] Ratings and reviews
- [x] Role-based dashboards with charts
- [x] Dark / light mode
- [x] Delete job with cascade cleanup
- [ ] Job expiry / auto-close (`is_active` + `expires_at`)
- [ ] `Completed` application status tied to job closure
- [ ] Profile photo upload
- [ ] Edit profile page
- [ ] Radius-based job matching
- [ ] Real-time push notifications
- [ ] Mobile app (React Native)
- [ ] AI-based worker matching

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ using Flask &nbsp;·&nbsp; Bootstrap 5 &nbsp;·&nbsp; SQLAlchemy

</div>
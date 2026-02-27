# Labour Workforce Management System (LWMS)
📌 Project Overview

Labour Workforce Management System (LWMS) is a web-based platform built using Flask that connects contractors and labour workers in a structured and efficient manner. The system enables contractors to post job opportunities and allows labourers to discover, filter, and accept jobs based on location and preferences.

This platform focuses on structured workforce coordination, job tracking, and performance monitoring.


🎯 Objectives

Digitize labour workforce coordination

Simplify contractor–labour communication

Enable location-based job filtering

Maintain structured worker performance records

Automate notifications and job status tracking


👥 User Roles
1. Contractor

Register/Login

Post job contracts (wage, hours, workers required, work type, date, location)

View applicants

Confirm attendance

Track job status

Rate workers after job completion



2. Labour

Register/Login

Maintain profile (city, pincode, work type)

View jobs

Filter jobs by:

City

Pincode

Wage range

Work type

Date

Accept job requests

Confirm attendance

View ratings

Receive notifications for new jobs in their city



🔔 Notification System

When a contractor posts a new job:

All labour users in the same city receive a notification.

Notifications appear on the labour dashboard.

Users can mark notifications as read.

This system is database-driven and does not rely on external push notification services.



📊 Additional Features

Email notifications (optional enhancement)

Job status tracking (Pending / Accepted / Completed)

Worker performance dashboard

Number of jobs completed

Average rating

Attendance consistency

Map embedding for job location visualization

Secure authentication using hashed passwords

REST-based architecture with proper HTTP status codes



🛠 Technology Stack

Backend: Flask (Python)

Database: SQLAlchemy (SQLite/MySQL)

Frontend: HTML, CSS, Bootstrap

Authentication: Flask-Login

Optional: Flask-Mail for email notifications

Map Embedding: Google Maps Embed



🚀 Future Scope

Radius-based job matching 

Real-time push notifications

AI-based workforce matching

Mobile application integration

Dynamic wage optimization

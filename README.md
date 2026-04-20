FairShare - Group Project Accountability System

📌 Project Overview

FairShare is a full-stack web application designed to track individual contributions in group projects and calculate fairness scores for each team member. It helps educators, project managers, and team leads identify inactive members and reward top contributors through an automated accountability system.

---

🎯 Problem Statement

In academic and professional group projects, it's often difficult to:

· Track who contributed what
· Identify members who aren't pulling their weight
· Quantify individual contributions fairly
· Provide objective feedback for grading or evaluation

FairShare solves this by providing a transparent, data-driven accountability system.

---

✨ Key Features

1. User Authentication

· Secure signup/login/logout system
· Password hashing with Werkzeug
· Session management with Flask-Login

2. Project Management

· Create projects with name, description, and deadline
· Add/remove team members by email
· View all projects in a clean dashboard

3. Task Management

· Create tasks with title, description, deadline, and priority (Low/Medium/High)
· Assign tasks to specific team members
· Update task status (Not Started, In Progress, Completed)
· Track task progress with percentage (0-100%)

4. Fairness Score Algorithm (Core Feature)

The fairness score is calculated using a weighted formula:

Component Weight Description
Tasks Completed 40% Percentage of assigned tasks finished
On-time Submissions 30% Tasks completed before deadline
Activity Level 20% Frequency of updates (last 30 days)
Peer Ratings 10% Average rating from teammates (1-5)

Score Categories:

· 80-100% → Top Contributor 🏆
· 50-79% → Average 👤
· Below 50% → Needs Improvement ⚠️

5. Peer Review System

· Rate teammates anonymously (1-5 stars)
· Add optional comments
· Prevent self-rating
· Average rating contributes to fairness score

6. Activity Tracking & Alerts

· Automatic logging of all task updates
· "Lazy Member Alert" for users inactive for 7+ days
· Real-time activity feed

7. Analytics Dashboard

· Task completion statistics
· Member performance comparison
· Activity timeline visualization

8. Notification System

· Real-time alerts when tasks are completed
· Team-wide notifications for important updates

---

🛠️ Technology Stack

Layer Technology
Backend Python 3.11, Flask
Database SQLite with SQLAlchemy ORM
Frontend HTML5, CSS3, Vanilla JavaScript
Authentication Flask-Login, Werkzeug
Styling Custom CSS (modern SaaS design)
Template Engine Jinja2

---

📊 Database Schema

```
users (id, name, email, password_hash, created_at)
projects (id, name, description, deadline, owner_id, created_at)
project_members (id, user_id, project_id, joined_at)
tasks (id, title, description, assigned_to, status, deadline, priority, project_id, progress)
activity_logs (id, user_id, task_id, project_id, action, timestamp)
peer_ratings (id, rater_id, rated_user_id, project_id, rating, comment)
notifications (id, user_id, project_id, message, read, created_at)
```

---

🚀 Installation & Setup

```bash
# Clone or create project
mkdir FairShare && cd FairShare

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "SECRET_KEY=your-secret-key" > .env

# Initialize database and seed sample data
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     exit()
>>> python3 seed.py

# Run the application
python3 app.py
```

Access at: http://localhost:5000

---

📁 Project Structure

```
FairShare/
├── app.py                 # Main application entry point
├── extensions.py          # DB and LoginManager instances
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── seed.py                # Sample data generator
├── models/                # Database models
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── activity.py
│   ├── peer_rating.py
│   └── notification.py
├── routes/                # Flask route handlers
│   ├── auth.py
│   ├── projects.py
│   ├── tasks.py
│   ├── peer_reviews.py
│   └── analytics.py
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── projects/
│   ├── tasks/
│   └── reviews/
├── static/                # CSS and JS files
│   ├── css/style.css
│   └── js/main.js
└── database/              # SQLite database file
```

---

👥 Use Cases

1. Academic Group Projects - Professors can track individual contributions
2. Software Development Teams - Scrum masters can monitor sprint progress
3. Remote Teams - Managers can identify inactive members
4. Hackathons - Organizers can evaluate team performance

---

🔮 Future Enhancements

· 📧 Email Notifications - Automated alerts for deadlines and inactivity
· 📎 File Attachments - Upload files to tasks
· 💬 Comments System - Discuss tasks within the platform
· 📊 Export Reports - Download project reports as PDF/CSV
· 🔄 Real-time Updates - WebSocket integration for live activity
· 📱 Mobile App - React Native companion app
· 🤖 AI Predictions - ML model to predict project success
· 🔗 GitHub Integration - Auto-track code contributions

---

🏆 Key Achievements

· ✅ Built a fully functional accountability system from scratch
· ✅ Implemented a weighted fairness algorithm with multiple metrics
· ✅ Created a clean, professional UI inspired by modern SaaS products
· ✅ Designed a scalable database schema with proper relationships
· ✅ Solved circular import issues using application factory pattern
· ✅ Achieved complete CRUD functionality for projects and tasks

---

📝 Sample Test Accounts

Email Password Role
alice@example.com password123 Project Owner
bob@example.com password123 Team Member
charlie@example.com password123 Team Member

---
 Contributing

Feel free to fork this project and submit pull requests for improvements!

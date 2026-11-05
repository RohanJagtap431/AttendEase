# AttendEase – Student Attendance Management System

AttendEase is a web-based Student Attendance Management System developed using Python and Django. It provides separate portals for administrators, teachers, and students to manage and monitor academic attendance.

## 🚀 Live Demo

**Live Website:** https://attendease-vam6.onrender.com/

**GitHub Repository:** https://github.com/RohanJagtap431/AttendEase

## ✨ Features

### Admin Portal
- Admin Dashboard
- Teacher Management
- Student Management
- Classroom Management
- Subject Management
- Teacher Assignment Management
- Attendance Monitoring
- System Overview

### Teacher Portal
- Teacher Dashboard
- View Assigned Classes and Subjects
- Mark Student Attendance
- View Attendance Records
- Generate Attendance Reports
- Export Attendance Reports to Excel and PDF

### Student Portal
- Student Dashboard
- View Personal Profile
- View Attendance History
- Subject-wise Attendance Statistics
- Overall Attendance Percentage

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Django | Web Framework |
| HTML5 | Page Structure |
| CSS3 | Styling and Responsive UI |
| JavaScript | Frontend Interactions |
| PostgreSQL | Database |
| SQLite | Local Development (if configured) |
| Git & GitHub | Version Control |
| Render | Deployment |
| Neon | Cloud PostgreSQL Database |

## 📂 Project Structure

```text
AttendEase/
│
├── accounts/
├── academics/
├── attendance/
├── dashboard/
├── students/
├── config/
│
├── templates/
│   ├── accounts/
│   ├── admin/
│   ├── teacher/
│   ├── student/
│   └── attendance/
│
├── static/
│   ├── css/
│   └── js/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/RohanJagtap431/AttendEase.git
```

### 2. Open Project Folder

```bash
cd AttendEase
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=your-database-url
CSRF_TRUSTED_ORIGINS=
```

Do not upload your actual `.env` file or database credentials to GitHub.

### 7. Apply Database Migrations

```bash
python manage.py migrate
```

### 8. Create Admin Account

```bash
python manage.py createsuperuser
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Open in browser:

```text
http://127.0.0.1:8000/
```

## 🔐 User Roles

| Role | Access |
|---|---|
| Admin | Manage and monitor the system |
| Teacher | Manage assigned classes and attendance |
| Student | View personal attendance and profile |

## 🎯 Project Objective

The main objective of AttendEase is to simplify student attendance management by providing a centralized web-based platform for administrators, teachers, and students.

## 👨‍💻 Developer

**Rohan Jagtap**

B.Sc. Computer Science Student

GitHub: https://github.com/RohanJagtap431

---

*AttendEase – Making Attendance Management Easier.*

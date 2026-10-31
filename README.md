# MYpart – My Society, My Responsibility

**A Civic Issue Reporting Platform**

🌐 **Live Website:** https://mypart-civic-reporting.onrender.com

## 📌 About the Project

MYpart (My Society, My Responsibility) is a web-based civic issue reporting platform developed to encourage citizens to take responsibility for maintaining clean and healthy public spaces.

The platform allows citizens to report problems such as improper waste disposal, clogged drainage systems, and unhygienic public areas. Reports can include descriptions, location details, and photographs to help authorities understand and address the issues.

## 🎯 Problem Statement

Many local civic issues remain unresolved because citizens lack a simple and accessible way to report them and track their progress.

MYpart aims to bridge this gap by providing a centralized platform for reporting and monitoring community issues.

## ✨ Key Features

- **Public Issue Reporting:** Citizens can report civic problems without creating an account.
- **Location Selection:** Interactive map-based location selection.
- **Photo Upload:** Attach photographs to reports for better identification of issues.
- **Report Tracking:** Monitor the status of submitted reports.
- **Admin Authentication:** Secure login for administrators.
- **Admin Dashboard:** Manage and update reported issues.
- **Search and Filtering:** Find reports using keywords, issue categories, and status.
- **Report Statistics:** View summaries of total, reported, in-progress, and resolved issues.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Frontend structure |
| CSS3 | Styling and responsive design |
| JavaScript | Frontend interactions |
| Git & GitHub | Version control |
| Render | Cloud deployment |

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Keerthana-Sivanandan/mypart-civic-reporting.git
```

### 2. Navigate to the project directory

```bash
cd mypart-civic-reporting
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the Flask secret key

Set the `MYPART_SECRET_KEY` environment variable to a secure random value before running the application.

### 7. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## 🌍 Live Deployment

MYpart is deployed using Render.

**Visit:** https://mypart-civic-reporting.onrender.com

## 🚀 Project Objective

MYpart encourages community participation and promotes civic responsibility by making it easier for citizens to report public issues and monitor their resolution.

**My Society, My Responsibility – Every Report Makes a Difference.**

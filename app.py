
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
    abort
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps

import sqlite3
import os
import uuid
from datetime import datetime


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "MYPART_SECRET_KEY",
    "mypart-local-development-key"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "mypart.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

STATUSES = ["Reported", "In Progress", "Resolved"]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


# --------------------------------------------------
# ADMIN LOGIN CONFIGURATION
# --------------------------------------------------

ADMIN_USERNAME = os.environ.get("MYPART_ADMIN_USERNAME", "admin")

# Local development credentials:
# Username: admin
# Password: ChangeThisPassword123!
ADMIN_PASSWORD_HASH = os.environ.get(
    "MYPART_ADMIN_PASSWORD_HASH",
    generate_password_hash("ChangeThisPassword123!")
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------


def init_db():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Reported',
                photo TEXT,
                latitude REAL,
                longitude REAL
            )
        """)

        existing_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(reports)"
            ).fetchall()
        }

        if "status" not in existing_columns:
            conn.execute("""
                ALTER TABLE reports
                ADD COLUMN status TEXT NOT NULL DEFAULT 'Reported'
            """)

        if "photo" not in existing_columns:
            conn.execute("""
                ALTER TABLE reports
                ADD COLUMN photo TEXT
            """)

        if "latitude" not in existing_columns:
            conn.execute("""
                ALTER TABLE reports
                ADD COLUMN latitude REAL
            """)

        if "longitude" not in existing_columns:
            conn.execute("""
                ALTER TABLE reports
                ADD COLUMN longitude REAL
            """)

        conn.commit()

    finally:
        conn.close()


init_db()

# --------------------------------------------------
# ADMIN AUTHENTICATION
# --------------------------------------------------

def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            flash(
                "Please log in to access this feature.",
                "error"
            )
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# SUBMIT A CIVIC ISSUE
# --------------------------------------------------

@app.route("/submit-report", methods=["POST"])

def submit_report():
    issue = request.form.get("issue", "").strip()
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()

    # Read optional map coordinates.
    latitude_value = request.form.get("latitude", "").strip()
    longitude_value = request.form.get("longitude", "").strip()

    latitude = None
    longitude = None

    # Both coordinates must be supplied together.
    if latitude_value or longitude_value:
        try:
            if not latitude_value or not longitude_value:
                raise ValueError

            latitude = float(latitude_value)
            longitude = float(longitude_value)

            if (
                not (-90 <= latitude <= 90)
                or not (-180 <= longitude <= 180)
            ):
                raise ValueError

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid map coordinates. Please select the location again."
            }), 400

    if not issue or not location or not description:
        return jsonify({
            "success": False,
            "message": "Please fill in all required fields."
        }), 400

    photo_filename = None
    photo = request.files.get("photo")

    if photo and photo.filename:
        safe_original_name = secure_filename(photo.filename)

        if (
            not safe_original_name
            or not allowed_file(safe_original_name)
        ):
            return jsonify({
                "success": False,
                "message": (
                    "Please upload a PNG, JPG, JPEG, WEBP, or GIF image."
                )
            }), 400

        extension = safe_original_name.rsplit(".", 1)[1].lower()
        photo_filename = f"{uuid.uuid4().hex}.{extension}"
        photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)

        try:
            photo.save(photo_path)
        except OSError:
            return jsonify({
                "success": False,
                "message": "The photo could not be saved. Please try again."
            }), 500

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO reports (
                issue, location, description,
                created_at, status, photo,
                latitude, longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue,
            location,
            description,
            created_at,
            "Reported",
            photo_filename,
            latitude,
            longitude
        ))

        report_id = cursor.lastrowid
        conn.commit()

    except sqlite3.Error:
        conn.rollback()

        if photo_filename:
            photo_path = os.path.join(
                UPLOAD_FOLDER,
                photo_filename
            )

            if os.path.exists(photo_path):
                os.remove(photo_path)

        return jsonify({
            "success": False,
            "message": "The report could not be saved. Please try again."
        }), 500

    finally:
        conn.close()

    return jsonify({
        "success": True,
        "message": "Your issue has been reported successfully.",
        "report_id": report_id
    }),201
# SERVE UPLOADED PHOTOS
# --------------------------------------------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# --------------------------------------------------
# VIEW REPORTS DASHBOARD
# --------------------------------------------------

@app.route("/reports")
def view_reports():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    issue_filter = request.args.get("issue", "").strip()

    conn = get_db_connection()

    try:
        query = "SELECT * FROM reports WHERE 1=1"
        params = []

        # Search by issue, location, or description.
        if search:
            query += """
                AND (
                    issue LIKE ?
                    OR location LIKE ?
                    OR description LIKE ?
                )
            """

            search_term = f"%{search}%"
            params.extend([
                search_term,
                search_term,
                search_term
            ])

        # Filter by status.
        if status_filter in STATUSES:
            query += " AND status = ?"
            params.append(status_filter)

        # Filter by issue type.
        if issue_filter:
            query += " AND issue = ?"
            params.append(issue_filter)

        query += " ORDER BY id DESC"

        reports = conn.execute(
            query,
            params
        ).fetchall()

        # Calculate statistics across all reports.
        total_reports = conn.execute(
            "SELECT COUNT(*) FROM reports"
        ).fetchone()[0]

        reported_count = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE status = ?",
            ("Reported",)
        ).fetchone()[0]

        in_progress_count = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE status = ?",
            ("In Progress",)
        ).fetchone()[0]

        resolved_count = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE status = ?",
            ("Resolved",)
        ).fetchone()[0]

        issue_types = conn.execute("""
            SELECT DISTINCT issue
            FROM reports
            ORDER BY issue
        """).fetchall()

        # Required by the counts.* expressions in the dashboard template.
        counts = {
            "total": total_reports,
            "reported": reported_count,
            "in_progress": in_progress_count,
            "resolved": resolved_count
        }

    finally:
        conn.close()

    # CORRECT TEMPLATE NAME: reports.html
    return render_template(
        "reports.html",
        reports=reports,
        counts=counts,
        issue_types=issue_types,
        statuses=STATUSES,
        search=search,
        status_filter=status_filter,
        issue_filter=issue_filter
    )


# --------------------------------------------------
# VIEW FULL DETAILS OF ONE REPORT
# --------------------------------------------------

@app.route("/report/<int:report_id>")
def report_detail(report_id):
    conn = get_db_connection()

    try:
        report = conn.execute("""
            SELECT *
            FROM reports
            WHERE id = ?
        """, (report_id,)).fetchone()

    finally:
        conn.close()

    if report is None:
        abort(404)

    return render_template(
        "report_detail.html",
        report=report,
        statuses=STATUSES
    )


# --------------------------------------------------
# UPDATE REPORT STATUS — ADMIN ONLY
# --------------------------------------------------

@app.route(
    "/update-status/<int:report_id>",
    methods=["POST"]
)
@admin_required
def update_status(report_id):
    new_status = request.form.get("status", "").strip()

    if new_status not in STATUSES:
        flash("Invalid report status.", "error")
        return redirect(url_for(
            "report_detail",
            report_id=report_id
        ))

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE reports
            SET status = ?
            WHERE id = ?
        """, (new_status, report_id))

        conn.commit()

        if cursor.rowcount == 0:
            flash("Report not found.", "error")
            return redirect(url_for("view_reports"))

    except sqlite3.Error:
        conn.rollback()
        flash(
            "Unable to update the report status.",
            "error"
        )

    else:
        flash(
            f"Report #{report_id} status updated to {new_status}.",
            "success"
        )

    finally:
        conn.close()

    return redirect(url_for(
        "report_detail",
        report_id=report_id
    ))


# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("is_admin"):
        return redirect(url_for("view_reports"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and check_password_hash(
                ADMIN_PASSWORD_HASH,
                password
            )
        ):
            session.clear()
            session["is_admin"] = True

            flash("Login successful.", "success")
            return redirect(url_for("view_reports"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# --------------------------------------------------
# ADMIN LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# --------------------------------------------------
# FILE TOO LARGE ERROR
# --------------------------------------------------

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    if request.path == "/submit-report":
        return jsonify({
            "success": False,
            "message": (
                "The uploaded file is too large. Maximum size is 5 MB."
            )
        }), 413

    return "File too large. Maximum upload size is 5 MB.", 413


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

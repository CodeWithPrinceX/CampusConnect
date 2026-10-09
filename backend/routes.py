
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from database import get_connection

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

VALID_STATUSES = {"Open", "In Progress", "Resolved"}


# -------------------------
# Request Models
# -------------------------

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    department: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class IssueRequest(BaseModel):
    title: str
    category: str
    location: str
    description: str


class StatusUpdateRequest(BaseModel):
    status: str


# -------------------------
# Test Route
# -------------------------

@router.get("/test")
def test():
    return {"message": "Routes are working!"}


# -------------------------
# Register
# -------------------------

@router.post("/register", status_code=201)
def register(user: RegisterRequest):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        password_hash = pwd_context.hash(user.password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (user.full_name, user.email, password_hash)
        )

        connection.commit()

        return {
            "message": "Registration successful!",
            "user_id": cursor.lastrowid,
            "name": user.full_name,
            "email": user.email
        }

    except Exception as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(
                status_code=409,
                detail="This email is already registered."
            )

        raise HTTPException(
            status_code=500,
            detail="Registration failed."
        )

    finally:
        connection.close()


# -------------------------
# Login
# -------------------------

@router.post("/login")
def login(user: LoginRequest):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, password_hash
            FROM users
            WHERE email = ?
            """,
            (user.email,)
        )

        existing_user = cursor.fetchone()

    finally:
        connection.close()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    user_id, name, password_hash = existing_user

    if not pwd_context.verify(user.password, password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "message": "Login successful!",
        "user_id": user_id,
        "name": name,
        "email": user.email
    }


# -------------------------
# Create Issue
# -------------------------

@router.post("/issues", status_code=201)
def create_issue(issue: IssueRequest, user_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        cursor.execute(
            """
            INSERT INTO issues
                (user_id, category, title, description, location)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                issue.category,
                issue.title,
                issue.description,
                issue.location
            )
        )

        connection.commit()
        issue_id = cursor.lastrowid

        return {
            "message": "Issue created successfully!",
            "issue_id": issue_id,
            "location": issue.location,
            "status": "Open"
        }

    finally:
        connection.close()


# -------------------------
# Get All Issues
# -------------------------

@router.get("/issues")
def get_issues():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                i.id,
                i.user_id,
                i.title,
                i.category,
                i.description,
                i.location,
                i.status,
                i.created_at,
                u.name
            FROM issues AS i
            JOIN users AS u ON i.user_id = u.id
            ORDER BY i.id DESC
            """
        )

        rows = cursor.fetchall()

        issues = [
            {
                "id": row[0],
                "user_id": row[1],
                "title": row[2],
                "category": row[3],
                "description": row[4],
                "location": row[5],
                "status": row[6],
                "created_at": row[7],
                "reporter": row[8]
            }
            for row in rows
        ]

        return {
            "message": "Issues retrieved successfully!",
            "issues": issues
        }

    finally:
        connection.close()


# -------------------------
# Get Single Issue
# -------------------------

@router.get("/issues/{issue_id}")
def get_issue(issue_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                i.id,
                i.user_id,
                i.title,
                i.category,
                i.description,
                i.location,
                i.status,
                i.created_at,
                u.name
            FROM issues AS i
            JOIN users AS u ON i.user_id = u.id
            WHERE i.id = ?
            """,
            (issue_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Issue not found."
            )

        return {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "category": row[3],
            "description": row[4],
            "location": row[5],
            "status": row[6],
            "created_at": row[7],
            "reporter": row[8]
        }

    finally:
        connection.close()


# -------------------------
# Update Issue Status
# -------------------------

@router.put("/issues/{issue_id}/status")
def update_issue_status(
    issue_id: int,
    data: StatusUpdateRequest
):
    if data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Status must be Open, In Progress, or Resolved."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE issues
            SET status = ?
            WHERE id = ?
            """,
            (data.status, issue_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Issue not found."
            )

        connection.commit()

        return {
            "message": "Issue status updated successfully!",
            "issue_id": issue_id,
            "status": data.status
        }

    finally:
        connection.close()


# -------------------------
# Get User Profile
# -------------------------

@router.get("/profile/{user_id}")
def get_profile(user_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        cursor.execute(
            "SELECT COUNT(*) FROM issues WHERE user_id = ?",
            (user_id,)
        )

        issue_count = cursor.fetchone()[0]

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "total_issues": issue_count
        }

    finally:
        connection.close()

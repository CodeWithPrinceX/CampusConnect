from fastapi import APIRouter
from pydantic import BaseModel
from passlib.context import CryptContext
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import get_connection

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------------
# Test Route
# -------------------------

@router.get("/test")
def test():
    return {"message": "Routes are working!"}


# -------------------------
# Register
# -------------------------

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    department: str
    password: str


@router.post("/register")
def register(user: RegisterRequest):
    password_hash = pwd_context.hash(user.password)

    connection = get_connection()
    cursor = connection.cursor()

    try:
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
            "user_id": cursor.lastrowid
        }

    except Exception as e:
        return {
            "message": "Registration failed!",
            "error": str(e)
        }

    finally:
        connection.close()


# -------------------------
# Login
# -------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(user: LoginRequest):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, password_hash FROM users WHERE email = ?",
        (user.email,)
    )

    existing_user = cursor.fetchone()
    connection.close()

    if existing_user is None:
        return {"message": "Invalid email or password"}

    user_id, name, password_hash = existing_user

    if not pwd_context.verify(user.password, password_hash):
        return {"message": "Invalid email or password"}

    return {
        "message": "Login successful!",
        "user_id": user_id,
        "name": name,
        "email": user.email
    }


# -------------------------
# Create Issue
# -------------------------

class IssueRequest(BaseModel):
    title: str
    category: str
    location: str
    description: str


@router.post("/issues")
def create_issue(issue: IssueRequest):
    return {
        "message": "Issue data received!",
        "issue": issue
    }


# -------------------------
# Get All Issues
# -------------------------

@router.get("/issues")
def get_issues():
    return {
        "message": "Issues retrieved successfully!",
        "issues": []
    }


# -------------------------
# Get Single Issue
# -------------------------

@router.get("/issues/{issue_id}")
def get_issue(issue_id: int):
    return {
        "message": "Issue retrieved successfully!",
        "issue": {
            "id": issue_id,
            "title": "Sample Issue",
            "category": "Electrical",
            "location": "Block A",
            "description": "Sample issue description",
            "status": "Open"
        }
    }


# -------------------------
# Update Issue Status
# -------------------------

class StatusUpdateRequest(BaseModel):
    status: str


@router.put("/issues/{issue_id}/status")
def update_issue_status(issue_id: int, data: StatusUpdateRequest):
    return {
        "message": "Issue status updated successfully!",
        "issue_id": issue_id,
        "status": data.status
    }
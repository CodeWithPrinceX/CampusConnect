from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/test")
def test():
    return {"message": "Routes are working!"}


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    department: str
    password: str


@router.post("/register")
def register(user: RegisterRequest):
    return {
        "message": "Registration data received!",
        "user": user
    }


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(user: LoginRequest):
    return {
        "message": "Login data received!",
        "email": user.email
    }


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


@router.get("/issues")
def get_issues():
    return {
        "message": "Issues retrieved successfully!",
        "issues": []
    }


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
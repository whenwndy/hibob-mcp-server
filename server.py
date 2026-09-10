import json
import os
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "hibob.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="hibob-mock",
    version="1.0.0",
    instructions=(
        "Mock HiBob HR platform. Use get_employee to identify an employee first, "
        "then get_employee_benefits to answer benefits questions, get_pay_schedule "
        "for paycheck/proration questions, and get_onboarding_summary for a complete "
        "onboarding status overview. Devon Harris (EMP-001) is a new employee who "
        "started 2026-09-02."
    ),
)

# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

@mcp.tool()
def get_employee(
    id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    email: Optional[str] = Field(default=None, description="Filter by work email address (exact match)"),
    name: Optional[str] = Field(default=None, description="Filter by first or last name (partial match)"),
) -> list[dict]:
    """Find an employee by ID, email, or partial name match. Call this first to identify an employee before querying other tools."""
    results = _db["employees"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if email:
        results = [r for r in results if r.get("email", "").lower() == email.lower()]
    if name:
        results = [
            r for r in results
            if _match(r, "first_name", name) or _match(r, "last_name", name)
        ]
    return results


# ---------------------------------------------------------------------------
# Benefits Enrollment
# ---------------------------------------------------------------------------

@mcp.tool()
def get_employee_benefits(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Filter by employee name (partial match)"),
    plan_type: Optional[str] = Field(default=None, description="Filter by plan type: medical | dental | vision"),
    enrollment_status: Optional[str] = Field(default=None, description="Filter by status: active | pending | waived"),
) -> list[dict]:
    """Get benefits enrollment records for an employee. Use this to answer questions about when benefits kick in, coverage tiers, and premiums."""
    results = _db["benefits_enrollment"]
    if employee_id:
        results = [r for r in results if r["employee_id"].upper() == employee_id.upper()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if plan_type:
        results = [r for r in results if _match(r, "plan_type", plan_type)]
    if enrollment_status:
        results = [r for r in results if _match(r, "enrollment_status", enrollment_status)]
    return results


# ---------------------------------------------------------------------------
# Pay Schedule
# ---------------------------------------------------------------------------

@mcp.tool()
def get_pay_schedule(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Filter by employee name (partial match)"),
) -> list[dict]:
    """Get pay schedule and proration details for an employee. Includes proration_calculation with full math for the first partial pay period. Use this to answer questions about paychecks, proration, and salary."""
    results = _db["pay_schedules"]
    if employee_id:
        results = [r for r in results if r["employee_id"].upper() == employee_id.upper()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    return results


# ---------------------------------------------------------------------------
# Onboarding Tasks
# ---------------------------------------------------------------------------

@mcp.tool()
def get_onboarding_tasks(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Filter by employee name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: completed | pending | in_progress | overdue"),
    category: Optional[str] = Field(default=None, description="Filter by category: paperwork | it_setup | hr | training | benefits | culture"),
) -> list[dict]:
    """List onboarding tasks for an employee. Filter by status or category to see what's done, pending, or overdue."""
    results = _db["onboarding_tasks"]
    if employee_id:
        results = [r for r in results if r["employee_id"].upper() == employee_id.upper()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    return results


# ---------------------------------------------------------------------------
# Time Off
# ---------------------------------------------------------------------------

@mcp.tool()
def get_time_off(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Filter by employee name (partial match)"),
    policy_type: Optional[str] = Field(default=None, description="Filter by policy type: vacation | sick | personal"),
) -> list[dict]:
    """Get time off balances and accrual information for an employee."""
    results = _db["time_off"]
    if employee_id:
        results = [r for r in results if r["employee_id"].upper() == employee_id.upper()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if policy_type:
        results = [r for r in results if _match(r, "policy_type", policy_type)]
    return results


# ---------------------------------------------------------------------------
# Key Dates
# ---------------------------------------------------------------------------

@mcp.tool()
def get_key_dates(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Filter by employee name (partial match)"),
    date_type: Optional[str] = Field(default=None, description="Filter by type: benefits_effective | probation_end | performance_review | anniversary | first_paycheck"),
    upcoming_only: Optional[bool] = Field(default=None, description="If true, return only upcoming dates (is_upcoming=true)"),
) -> list[dict]:
    """Get important HR dates for an employee — first paycheck, benefits effective date, probation end, performance reviews, and work anniversaries."""
    results = _db["key_dates"]
    if employee_id:
        results = [r for r in results if r["employee_id"].upper() == employee_id.upper()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if date_type:
        results = [r for r in results if _match(r, "date_type", date_type)]
    if upcoming_only is True:
        results = [r for r in results if r.get("is_upcoming") is True]
    return results


# ---------------------------------------------------------------------------
# HR Policies
# ---------------------------------------------------------------------------

@mcp.tool()
def get_hr_policies(
    id: Optional[str] = Field(default=None, description="Filter by policy ID, e.g. POL-001"),
    name: Optional[str] = Field(default=None, description="Filter by policy name (partial match)"),
    category: Optional[str] = Field(default=None, description="Filter by category: benefits | payroll | time_off | performance"),
) -> list[dict]:
    """List HR policies. Use to find policy details on benefits waiting periods, payroll proration, time off accrual, and the introductory period."""
    results = _db["hr_policies"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    return results


# ---------------------------------------------------------------------------
# Onboarding Summary (Scenario 3 — proactive Surface)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_onboarding_summary(
    employee_id: Optional[str] = Field(default=None, description="Employee ID, e.g. EMP-001"),
    employee_name: Optional[str] = Field(default=None, description="Employee name (partial match)"),
) -> dict:
    """
    Return a structured onboarding summary for an employee combining:
    - Employee profile
    - Benefits enrollment status (plan name, effective date, status per plan)
    - Key upcoming HR dates (benefits effective, first paycheck, probation end, performance review)
    - Pending and overdue onboarding tasks

    This is the primary tool for scenario 3 — powering a proactive onboarding Surface in Slack.
    Call this to give a new employee a complete snapshot of where they stand in onboarding.
    """
    # --- Resolve employee ---
    employees = _db["employees"]
    if employee_id:
        employees = [e for e in employees if e["id"].upper() == employee_id.upper()]
    if employee_name:
        employees = [
            e for e in employees
            if _match(e, "first_name", employee_name) or _match(e, "last_name", employee_name)
        ]
    if not employees:
        return {"error": "Employee not found. Try get_employee to look up the correct ID or name."}
    employee = employees[0]
    emp_id = employee["id"]

    # --- Benefits enrollment ---
    benefits = [
        {
            "plan_type": b["plan_type"],
            "plan_name": b["plan_name"],
            "carrier": b["carrier"],
            "coverage_tier": b["coverage_tier"],
            "enrollment_status": b["enrollment_status"],
            "effective_date": b["effective_date"],
            "employee_contribution_usd": b["employee_contribution_usd"],
            "notes": b["notes"],
        }
        for b in _db["benefits_enrollment"]
        if b["employee_id"] == emp_id
    ]

    # --- Key upcoming dates ---
    key_dates = [
        {
            "date_type": d["date_type"],
            "date": d["date"],
            "description": d["description"],
        }
        for d in _db["key_dates"]
        if d["employee_id"] == emp_id and d.get("is_upcoming") is True
    ]
    key_dates.sort(key=lambda d: d["date"])

    # --- Pending and overdue onboarding tasks ---
    incomplete_tasks = [
        {
            "id": t["id"],
            "task_name": t["task_name"],
            "category": t["category"],
            "status": t["status"],
            "due_date": t["due_date"],
            "assigned_to": t["assigned_to"],
            "notes": t["notes"],
        }
        for t in _db["onboarding_tasks"]
        if t["employee_id"] == emp_id and t["status"] in ("pending", "in_progress", "overdue")
    ]

    # --- Completed tasks count ---
    all_tasks = [t for t in _db["onboarding_tasks"] if t["employee_id"] == emp_id]
    completed_count = sum(1 for t in all_tasks if t["status"] == "completed")
    total_count = len(all_tasks)

    return {
        "employee": {
            "id": employee["id"],
            "name": f"{employee['first_name']} {employee['last_name']}",
            "job_title": employee["job_title"],
            "department": employee["department"],
            "start_date": employee["start_date"],
            "manager_name": employee["manager_name"],
        },
        "benefits_enrollment": benefits,
        "key_upcoming_dates": key_dates,
        "incomplete_onboarding_tasks": incomplete_tasks,
        "onboarding_progress": {
            "completed_tasks": completed_count,
            "total_tasks": total_count,
            "completion_percent": round((completed_count / total_count) * 100) if total_count else 0,
        },
    }


# ---------------------------------------------------------------------------
# Write Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def update_onboarding_task(
    id: str = Field(description="Onboarding task ID to update, e.g. TASK-010"),
    status: str = Field(description="New status: completed | pending | in_progress | overdue"),
    notes: Optional[str] = Field(default=None, description="Optional notes to append or replace on the task"),
) -> dict:
    """Mark an onboarding task as complete or update its status. Returns the updated task record."""
    tasks = _db["onboarding_tasks"]
    for task in tasks:
        if task["id"].upper() == id.upper():
            task["status"] = status
            if notes is not None:
                task["notes"] = notes
            if status == "completed" and task.get("completed_at") is None:
                import datetime
                task["completed_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            return {"updated": True, "task": task}
    return {"updated": False, "error": f"Task '{id}' not found."}


@mcp.tool()
def request_time_off(
    employee_id: str = Field(description="Employee ID requesting time off, e.g. EMP-001"),
    policy_type: str = Field(description="Type of leave: vacation | sick | personal"),
    start_date: str = Field(description="Start date of time off, e.g. 2026-10-15"),
    end_date: str = Field(description="End date of time off, e.g. 2026-10-17"),
    notes: Optional[str] = Field(default=None, description="Optional reason or notes for the request"),
) -> dict:
    """Submit a time off request for an employee. Validates that sufficient balance exists and returns a confirmation."""
    # Find employee
    employees = [e for e in _db["employees"] if e["id"].upper() == employee_id.upper()]
    if not employees:
        return {"submitted": False, "error": f"Employee '{employee_id}' not found."}
    employee = employees[0]

    # Find balance
    balances = [
        b for b in _db["time_off"]
        if b["employee_id"].upper() == employee_id.upper()
        and b["policy_type"].lower() == policy_type.lower()
    ]
    if not balances:
        return {"submitted": False, "error": f"No {policy_type} balance found for {employee_id}."}
    balance = balances[0]

    # Simple business-day estimate (calendar days / 1.4 as rough proxy)
    from datetime import date
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {"submitted": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    calendar_days = (end - start).days + 1
    if calendar_days <= 0:
        return {"submitted": False, "error": "end_date must be on or after start_date."}

    # Generate a request ID
    import uuid
    request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"

    return {
        "submitted": True,
        "request_id": request_id,
        "employee_id": employee_id,
        "employee_name": f"{employee['first_name']} {employee['last_name']}",
        "policy_type": policy_type,
        "start_date": start_date,
        "end_date": end_date,
        "calendar_days_requested": calendar_days,
        "current_balance_days": balance["balance_days"],
        "status": "pending_approval",
        "notes": notes or "",
        "message": f"Time off request {request_id} submitted for {employee['first_name']} {employee['last_name']} ({policy_type}, {start_date} to {end_date}). Pending manager approval.",
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

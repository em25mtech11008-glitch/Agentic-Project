"""
==================================================
ENTERPRISE MCP TOOLS — Specialized Agent Tools
==================================================

Educational Comment:
This module contains specialized MCP tools designed for specific agents.
Instead of forcing every agent to write raw MongoDB JSON queries, we provide
high-level, purpose-built tools that wrap common operations.

WHY specialized tools instead of raw queries?
1. RELIABILITY: The AI doesn't need to guess field names or query syntax.
2. SAFETY: We control exactly what data is returned and how much.
3. SPEED: Pre-built queries execute faster than the AI figuring out the schema.
4. AUDITABILITY: Each tool has a clear purpose that can be logged and traced.

HOW it works:
Each function is registered as an MCP tool via the @mcp.tool() decorator.
The MCP server exposes them over stdio, and the LangGraph worker_node
discovers them via mcp_client.get_tools(). The AI sees the tool name,
description, and parameter schema, then decides whether to call it.
"""

import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

# Reuse the same lazy MongoDB connection pattern from mongodb_tools.py
_mongo_client = None

def _get_db():
    """
    Educational Comment:
    Lazy initialization pattern — we only create the MongoDB connection
    the first time a tool is actually called, not at import time.
    This prevents connection errors from crashing the MCP server on startup
    if the URI is misconfigured.
    """
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri or "<username>" in uri:
            raise ValueError("MONGODB_URI is missing or invalid in .env")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


def register_enterprise_tools(mcp: FastMCP):
    """
    Registers all specialized enterprise tools to the provided MCP server instance.
    These tools are organized by the agent that primarily uses them,
    but any agent can call any tool if the AI COO determines it's relevant.
    """

    # ==========================================================
    # FINANCE AGENT TOOLS
    # ==========================================================

    @mcp.tool()
    async def get_overdue_invoices() -> str:
        """
        Retrieves all invoices with status 'Overdue' from the database.
        Returns: A JSON array of overdue invoices including client_name, amount_due, issue_date, and due_date.
        Used by: Finance Agent, Executive Agent.
        """
        try:
            db = _get_db()
            cursor = db.invoices.find({"status": "Overdue"}).limit(50)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            if not results:
                return "No overdue invoices found. All accounts are current."
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error fetching overdue invoices: {str(e)}"

    @mcp.tool()
    async def get_expense_report(category: str = "") -> str:
        """
        Generates an expense report grouped by category.
        If a category is provided (e.g., 'Travel', 'Software'), filters to that category only.
        Returns: A JSON summary with total spend per category and individual expense records.
        Used by: Finance Agent, Executive Agent.
        """
        try:
            db = _get_db()
            query_filter = {}
            if category:
                query_filter["category"] = category

            cursor = db.expenses.find(query_filter).limit(50)
            expenses = []
            category_totals = {}
            async for doc in cursor:
                doc.pop('_id', None)
                expenses.append(doc)
                cat = doc.get("category", "Uncategorized")
                category_totals[cat] = category_totals.get(cat, 0) + doc.get("amount", 0)

            summary = {
                "total_expenses": round(sum(category_totals.values()), 2),
                "by_category": {k: round(v, 2) for k, v in category_totals.items()},
                "record_count": len(expenses),
                "details": expenses[:10]  # Limit details to 10 to save context
            }
            return json.dumps(summary, indent=2, default=str)
        except Exception as e:
            return f"Error generating expense report: {str(e)}"

    @mcp.tool()
    async def get_revenue_summary() -> str:
        """
        Calculates total revenue from the payments collection.
        Breaks down revenue by payment type (credit_card, boleto, voucher, debit_card).
        Returns: A JSON object with total_revenue, breakdown_by_payment_type, and total_transactions.
        Used by: Finance Agent, Sales Agent, Executive Agent.
        """
        try:
            db = _get_db()
            cursor = db.payments.find({}).limit(500)
            total = 0
            by_type = {}
            count = 0
            async for doc in cursor:
                val = doc.get("payment_value", 0)
                total += val
                ptype = doc.get("payment_type", "unknown")
                by_type[ptype] = by_type.get(ptype, 0) + val
                count += 1

            summary = {
                "total_revenue": round(total, 2),
                "total_transactions": count,
                "breakdown_by_payment_type": {k: round(v, 2) for k, v in by_type.items()}
            }
            return json.dumps(summary, indent=2, default=str)
        except Exception as e:
            return f"Error calculating revenue: {str(e)}"

    # ==========================================================
    # SALES AGENT TOOLS
    # ==========================================================

    @mcp.tool()
    async def get_sales_pipeline() -> str:
        """
        Provides a sales pipeline summary by counting orders at each stage
        (delivered, shipped, processing, invoiced, canceled).
        Returns: A JSON object with order counts and values per status.
        Used by: Sales Agent, Executive Agent.
        """
        try:
            db = _get_db()
            cursor = db.orders.find({}).limit(500)
            pipeline = {}
            async for doc in cursor:
                status = doc.get("order_status", "unknown")
                if status not in pipeline:
                    pipeline[status] = {"count": 0, "order_ids": []}
                pipeline[status]["count"] += 1
                if len(pipeline[status]["order_ids"]) < 3:  # Keep sample IDs
                    pipeline[status]["order_ids"].append(doc.get("order_id", ""))

            return json.dumps({
                "pipeline_summary": pipeline,
                "total_orders": sum(v["count"] for v in pipeline.values())
            }, indent=2, default=str)
        except Exception as e:
            return f"Error fetching sales pipeline: {str(e)}"

    @mcp.tool()
    async def search_customers(city: str = "", state: str = "", limit: int = 10) -> str:
        """
        Searches the customers collection by city and/or state.
        If no filters are provided, returns a sample of customers.
        Args:
            city: Filter by customer city (optional).
            state: Filter by 2-letter state abbreviation (optional).
            limit: Max number of results (default 10, max 50).
        Used by: Sales Agent, Support Agent.
        """
        try:
            db = _get_db()
            query_filter = {}
            if city:
                query_filter["customer_city"] = {"$regex": city, "$options": "i"}
            if state:
                query_filter["customer_state"] = state.upper()

            limit = min(limit, 50)
            cursor = db.customers.find(query_filter).limit(limit)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            if not results:
                return "No customers found matching the criteria."
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error searching customers: {str(e)}"

    # ==========================================================
    # SUPPORT AGENT TOOLS
    # ==========================================================

    @mcp.tool()
    async def search_support_tickets(
        min_score: int = 0,
        max_score: int = 5,
        keyword: str = "",
        limit: int = 10
    ) -> str:
        """
        Searches the reviews collection which acts as a support ticket system.
        Filters by review_score range and optional keyword in the comment.
        Low scores (1-2) indicate unhappy customers that may need support escalation.
        Args:
            min_score: Minimum review score to include (1-5, default 0 = all).
            max_score: Maximum review score to include (1-5, default 5).
            keyword: Optional keyword to search in review comments.
            limit: Max results (default 10, max 50).
        Used by: Support Agent, Executive Agent.
        """
        try:
            db = _get_db()
            query_filter = {
                "review_score": {"$gte": min_score, "$lte": max_score}
            }
            if keyword:
                query_filter["review_comment_message"] = {
                    "$regex": keyword, "$options": "i"
                }

            limit = min(limit, 50)
            cursor = db.reviews.find(query_filter).limit(limit)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            if not results:
                return "No support tickets/reviews found matching the criteria."
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error searching support tickets: {str(e)}"

    # ==========================================================
    # OPERATIONS AGENT TOOLS
    # ==========================================================

    @mcp.tool()
    async def get_blocked_tasks() -> str:
        """
        Retrieves all tasks with status 'Blocked' or high-priority tasks
        (P0, P1) that are not yet 'Done'.
        Returns: A JSON array of critical tasks needing attention.
        Used by: Operations Agent, Executive Agent.
        """
        try:
            db = _get_db()
            # Find blocked tasks OR high-priority incomplete tasks
            cursor = db.tasks.find({
                "$or": [
                    {"status": "Blocked"},
                    {"priority": {"$in": ["P0", "P1"]}, "status": {"$ne": "Done"}}
                ]
            }).limit(50)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            if not results:
                return "No blocked or critical tasks found. Operations are running smoothly."
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error fetching blocked tasks: {str(e)}"

    @mcp.tool()
    async def get_operational_metrics() -> str:
        """
        Generates an operational dashboard showing task distribution
        by status (To Do, In Progress, Done, Blocked) and priority (P0-P3).
        Returns: A JSON object with counts per status and per priority.
        Used by: Operations Agent, Executive Agent.
        """
        try:
            db = _get_db()
            cursor = db.tasks.find({}).limit(500)
            by_status = {}
            by_priority = {}
            total = 0
            async for doc in cursor:
                total += 1
                status = doc.get("status", "Unknown")
                priority = doc.get("priority", "Unknown")
                by_status[status] = by_status.get(status, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1

            return json.dumps({
                "total_tasks": total,
                "by_status": by_status,
                "by_priority": by_priority,
                "completion_rate": f"{round(by_status.get('Done', 0) / max(total, 1) * 100, 1)}%"
            }, indent=2, default=str)
        except Exception as e:
            return f"Error fetching operational metrics: {str(e)}"

    # ==========================================================
    # HR AGENT TOOLS
    # ==========================================================

    @mcp.tool()
    async def lookup_employee(name: str = "", department: str = "") -> str:
        """
        Searches the employees collection by name and/or department.
        If no filters are provided, returns all employees.
        Args:
            name: Partial or full employee name to search (case-insensitive).
            department: Department name (e.g., 'Sales', 'Engineering', 'HR').
        NOTE: Salary information is included for authorized HR queries only.
        Used by: HR Agent.
        """
        try:
            db = _get_db()
            query_filter = {}
            if name:
                query_filter["name"] = {"$regex": name, "$options": "i"}
            if department:
                query_filter["department"] = {"$regex": department, "$options": "i"}

            cursor = db.employees.find(query_filter).limit(20)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            if not results:
                return "No employees found matching the criteria."
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error looking up employee: {str(e)}"

    @mcp.tool()
    async def get_department_summary() -> str:
        """
        Provides a summary of each department including headcount,
        average salary, and total expenses attributed to that department's employees.
        Returns: A JSON object with department-level aggregated metrics.
        Used by: HR Agent, Executive Agent.
        """
        try:
            db = _get_db()

            # Aggregate employees by department
            emp_cursor = db.employees.find({}).limit(200)
            departments = {}
            employee_ids = {}  # Map employee_id -> department
            async for doc in emp_cursor:
                dept = doc.get("department", "Unknown")
                if dept not in departments:
                    departments[dept] = {"headcount": 0, "total_salary": 0, "total_expenses": 0}
                departments[dept]["headcount"] += 1
                departments[dept]["total_salary"] += doc.get("salary", 0)
                employee_ids[doc.get("employee_id")] = dept

            # Aggregate expenses by department
            exp_cursor = db.expenses.find({}).limit(500)
            async for doc in exp_cursor:
                emp_id = doc.get("employee_id")
                if emp_id in employee_ids:
                    dept = employee_ids[emp_id]
                    departments[dept]["total_expenses"] += doc.get("amount", 0)

            # Calculate averages
            for dept, data in departments.items():
                if data["headcount"] > 0:
                    data["avg_salary"] = round(data["total_salary"] / data["headcount"], 2)
                data["total_salary"] = round(data["total_salary"], 2)
                data["total_expenses"] = round(data["total_expenses"], 2)

            return json.dumps(departments, indent=2, default=str)
        except Exception as e:
            return f"Error generating department summary: {str(e)}"

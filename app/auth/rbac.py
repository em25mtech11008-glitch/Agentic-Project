"""
==================================================
RBAC — Role-Based Access Control System
==================================================

Educational Comment:
This module defines the RBAC system for the AI Operations Command Center.
RBAC ensures that every user can only access the data and actions that their
role permits. This is enforced on the BACKEND — frontend route hiding is
cosmetic only and provides zero security.

HOW IT WORKS:
1. Each user has a `role` (e.g., "CEO", "FINANCE").
2. Each role maps to a set of granular `permissions` (e.g., "finance.view").
3. FastAPI middleware checks the user's role against the required permission
   before allowing access to any protected endpoint.
"""

from enum import Enum
from typing import Dict, Set


# ==================================================
# ROLES
# ==================================================
# Educational Comment:
# We use a string enum so roles are serializable to/from MongoDB and JWTs.
# Each role represents a job function in the startup.

class Role(str, Enum):
    CEO = "CEO"
    MANAGER = "MANAGER"
    FINANCE = "FINANCE"
    SALES = "SALES"
    SUPPORT = "SUPPORT"
    OPERATIONS = "OPERATIONS"
    HR = "HR"
    BUSINESS_ANALYST = "BUSINESS_ANALYST"
    EMPLOYEE = "EMPLOYEE"


# ==================================================
# PERMISSIONS
# ==================================================
# Educational Comment:
# Permissions are granular strings using dot notation (e.g., "finance.view").
# This allows us to grant fine-grained access. For example, a FINANCE user
# can view invoices but might not be allowed to execute refunds without
# CEO approval.

class Permission(str, Enum):
    # Dashboard
    DASHBOARD_VIEW = "dashboard.view"
    COMPANY_VIEW = "company.view"

    # Customers
    CUSTOMER_VIEW = "customer.view"
    CUSTOMER_UPDATE = "customer.update"

    # Sales
    SALES_VIEW = "sales.view"
    SALES_UPDATE = "sales.update"
    SALES_EXECUTE = "sales.execute"

    # Finance
    FINANCE_VIEW = "finance.view"
    FINANCE_CREATE_INVOICE = "finance.create_invoice"
    FINANCE_SEND_INVOICE = "finance.send_invoice"
    FINANCE_PREPARE_REFUND = "finance.prepare_refund"
    FINANCE_EXECUTE_PAYMENT = "finance.execute_payment"

    # Support
    SUPPORT_VIEW = "support.view"
    SUPPORT_UPDATE = "support.update"
    SUPPORT_RESPOND = "support.respond"
    SUPPORT_ESCALATE = "support.escalate"

    # Operations
    OPERATIONS_VIEW = "operations.view"
    OPERATIONS_CREATE_TASK = "operations.create_task"
    OPERATIONS_ASSIGN_TASK = "operations.assign_task"
    OPERATIONS_EXECUTE_WORKFLOW = "operations.execute_workflow"

    # HR
    HR_VIEW = "hr.view"
    HR_MANAGE_ONBOARDING = "hr.manage_onboarding"
    HR_MANAGE_LEAVE = "hr.manage_leave"

    # Analytics
    ANALYTICS_VIEW = "analytics.view"

    # Approvals
    APPROVALS_VIEW = "approvals.view"
    APPROVALS_APPROVE = "approvals.approve"
    APPROVALS_REJECT = "approvals.reject"

    # AI
    AI_VIEW = "ai.view"
    AI_EXECUTE = "ai.execute"

    # Admin
    USERS_MANAGE = "users.manage"
    ROLES_MANAGE = "roles.manage"
    INTEGRATIONS_MANAGE = "integrations.manage"

    # Audit
    AUDIT_VIEW = "audit.view"


# ==================================================
# ROLE → PERMISSION MAPPING
# ==================================================
# Educational Comment:
# This is the heart of RBAC. Each role is mapped to a set of permissions.
# When a user with role "FINANCE" hits an endpoint requiring "finance.view",
# we check if "finance.view" exists in ROLE_PERMISSIONS["FINANCE"].
# If yes → access granted. If no → 403 Forbidden.

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    Role.CEO: {
        # CEO has access to everything
        Permission.DASHBOARD_VIEW, Permission.COMPANY_VIEW,
        Permission.CUSTOMER_VIEW, Permission.CUSTOMER_UPDATE,
        Permission.SALES_VIEW, Permission.SALES_UPDATE, Permission.SALES_EXECUTE,
        Permission.FINANCE_VIEW, Permission.FINANCE_CREATE_INVOICE,
        Permission.FINANCE_SEND_INVOICE, Permission.FINANCE_PREPARE_REFUND,
        Permission.FINANCE_EXECUTE_PAYMENT,
        Permission.SUPPORT_VIEW, Permission.SUPPORT_UPDATE,
        Permission.SUPPORT_RESPOND, Permission.SUPPORT_ESCALATE,
        Permission.OPERATIONS_VIEW, Permission.OPERATIONS_CREATE_TASK,
        Permission.OPERATIONS_ASSIGN_TASK, Permission.OPERATIONS_EXECUTE_WORKFLOW,
        Permission.HR_VIEW, Permission.HR_MANAGE_ONBOARDING, Permission.HR_MANAGE_LEAVE,
        Permission.ANALYTICS_VIEW,
        Permission.APPROVALS_VIEW, Permission.APPROVALS_APPROVE, Permission.APPROVALS_REJECT,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.USERS_MANAGE, Permission.ROLES_MANAGE, Permission.INTEGRATIONS_MANAGE,
        Permission.AUDIT_VIEW,
    },
    Role.MANAGER: {
        Permission.DASHBOARD_VIEW, Permission.COMPANY_VIEW,
        Permission.CUSTOMER_VIEW, Permission.CUSTOMER_UPDATE,
        Permission.SALES_VIEW, Permission.SALES_UPDATE,
        Permission.SUPPORT_VIEW, Permission.SUPPORT_UPDATE,
        Permission.OPERATIONS_VIEW, Permission.OPERATIONS_CREATE_TASK,
        Permission.OPERATIONS_ASSIGN_TASK,
        Permission.APPROVALS_VIEW, Permission.APPROVALS_APPROVE, Permission.APPROVALS_REJECT,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.ANALYTICS_VIEW,
    },
    Role.FINANCE: {
        Permission.DASHBOARD_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.FINANCE_VIEW, Permission.FINANCE_CREATE_INVOICE,
        Permission.FINANCE_SEND_INVOICE, Permission.FINANCE_PREPARE_REFUND,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.APPROVALS_VIEW,
    },
    Role.SALES: {
        Permission.DASHBOARD_VIEW,
        Permission.CUSTOMER_VIEW, Permission.CUSTOMER_UPDATE,
        Permission.SALES_VIEW, Permission.SALES_UPDATE, Permission.SALES_EXECUTE,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.APPROVALS_VIEW,
    },
    Role.SUPPORT: {
        Permission.DASHBOARD_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.SUPPORT_VIEW, Permission.SUPPORT_UPDATE,
        Permission.SUPPORT_RESPOND, Permission.SUPPORT_ESCALATE,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.APPROVALS_VIEW,
    },
    Role.OPERATIONS: {
        Permission.DASHBOARD_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.OPERATIONS_VIEW, Permission.OPERATIONS_CREATE_TASK,
        Permission.OPERATIONS_ASSIGN_TASK, Permission.OPERATIONS_EXECUTE_WORKFLOW,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.APPROVALS_VIEW,
    },
    Role.HR: {
        Permission.DASHBOARD_VIEW,
        Permission.HR_VIEW, Permission.HR_MANAGE_ONBOARDING, Permission.HR_MANAGE_LEAVE,
        Permission.AI_VIEW, Permission.AI_EXECUTE,
        Permission.APPROVALS_VIEW,
    },
    Role.BUSINESS_ANALYST: {
        Permission.DASHBOARD_VIEW, Permission.COMPANY_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.SALES_VIEW,
        Permission.FINANCE_VIEW,
        Permission.SUPPORT_VIEW,
        Permission.OPERATIONS_VIEW,
        Permission.HR_VIEW,
        Permission.ANALYTICS_VIEW,
        Permission.AI_VIEW,
    },
    Role.EMPLOYEE: {
        Permission.DASHBOARD_VIEW,
        Permission.AI_VIEW,
        Permission.APPROVALS_VIEW,
    },
}


def has_permission(role: str, permission: str) -> bool:
    """
    Checks if a given role has the specified permission.
    Returns True if the role has the permission, False otherwise.
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms


def get_permissions_for_role(role: str) -> Set[str]:
    """
    Returns the full set of permissions for a given role.
    Useful for sending the user's permissions to the frontend
    so it can hide/show UI elements (cosmetic only — backend enforces).
    """
    return ROLE_PERMISSIONS.get(role, set())

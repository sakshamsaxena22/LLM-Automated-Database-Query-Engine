"""
Role-Based Access Control (RBAC) — Section 11.

Roles
-----
viewer      – read only
editor      – read, create, update
manager     – read, create, update, delete (own department)
admin       – all operations
super_admin – all + manage users/orgs

The ``RoleChecker`` class is a reusable FastAPI dependency.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, FrozenSet, List, Set

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """Application roles ordered by privilege."""

    viewer = "viewer"
    editor = "editor"
    manager = "manager"
    admin = "admin"
    super_admin = "super_admin"


# ── Permission matrix ─────────────────────────────────────────────────
ROLE_PERMISSIONS: Dict[Role, FrozenSet[str]] = {
    Role.viewer: frozenset({"read"}),
    Role.editor: frozenset({"read", "create", "update"}),
    Role.manager: frozenset({"read", "create", "update", "delete"}),
    Role.admin: frozenset({"read", "create", "update", "delete", "manage_data"}),
    Role.super_admin: frozenset(
        {"read", "create", "update", "delete", "manage_data", "manage_users", "manage_orgs"}
    ),
}


def has_permission(role: Role | str, operation: str) -> bool:
    """Return ``True`` if *role* may perform *operation*."""
    if isinstance(role, str):
        try:
            role = Role(role)
        except ValueError:
            return False
    return operation in ROLE_PERMISSIONS.get(role, frozenset())


def check_permission(role: Role | str, operation: str) -> None:
    """Raise ``PermissionError`` if *role* lacks *operation*."""
    if not has_permission(role, operation):
        raise PermissionError(f"Role '{role}' is not allowed to perform '{operation}'")


class RoleChecker:
    """FastAPI dependency that enforces role-based access.

    Usage::

        @router.get("/admin-only", dependencies=[Depends(RoleChecker(["admin", "super_admin"]))])
        async def admin_endpoint(): ...

    Or inject directly to get the user payload::

        async def handler(user=Depends(RoleChecker(["editor"]))):
            print(user["sub"])
    """

    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles: Set[str] = set(allowed_roles)

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        user_role: str = current_user.get("role", "")
        if user_role not in self.allowed_roles:
            logger.warning(
                "Access denied: user=%s role=%s required=%s",
                current_user.get("sub"),
                user_role,
                self.allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is not authorized for this resource",
            )
        return current_user

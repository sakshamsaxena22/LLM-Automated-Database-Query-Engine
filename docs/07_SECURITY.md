# Security Audit & Guardrails — LLM Real-Time Database Query Engine

This document details the multi-layered security controls, permission matrices, and token defense layers.

## 1. Multi-Tenant Role-Based Access Control (RBAC)

Hierarchical user permissions are managed via `backend/app/core/permissions.py`.

### Roles & Operations Matrix

| Role | Permissions | Operation Scope |
|------|-------------|-----------------|
| `viewer` | `read` | Read-only access to transaction queries. |
| `editor` | `read`, `create`, `update` | Add/update transactions (no deletes). |
| `manager` | `read`, `create`, `update`, `delete` | Operations scoped to the user's department/tenant. |
| `admin` | `read`, `create`, `update`, `delete`, `manage_data` | Edit dataset configurations. |
| `super_admin` | `read`, `create`, `update`, `delete`, `manage_data`, `manage_users`, `manage_orgs` | Create/disable users and manage tenant orgs. |

### Enforcements
* **`RoleChecker` Dependency**: Configured as an active FastAPI route dependency. Triggers HTTP 403 Forbidden errors if a user lacks the required roles.

---

## 2. Authentication & Tenancy Isolation

* **JWT Structure**: Uses HS256 signatures containing `sub` (User ID), `org_id` (Tenant ID), `role`, and `exp` claims.
* **Token Expiry**: Enforces 30 minutes expiration on access tokens and 7 days on refresh tokens.
* **Tenant Partitioning**:
  * Every repository and adapter call automatically appends the user's `org_id` from the JWT claims to database filters, preventing cross-tenant data leakage.

---

## 3. Query Execution & Injection Prevention

The system blocks direct execution of LLM outputs, running them through a validation pipeline:

```
LLM Output JSON
   │
   ├──▶ 1. Top-Level Whitelist Check (Only: 'filter', 'projection', 'sort', 'limit', 'pipeline')
   │
   ├──▶ 2. Dangerous Operator Check (Blocks: $where, $expr, $function, $merge, $out, $lookup, etc.)
   │
   ├──▶ 3. Target Schema Field Verification (Restricts fields to ALLOWED_FIELDS whitelist)
   │
   └──▶ 4. Pipeline Stage Guard (Restricts aggregation to: $match, $group, $sort, $limit, $skip, $project, etc.)
```

### Write Prevention & Risk Levels
* **High-Risk Actions**: Any deletion and any update without equality filters is assessed as `"high"` risk, requiring additional approval steps.
* **NoSQL Injection Block**: Recursively inspects nested filters and logical expressions for prohibited operators.

# Phase 4B: Role Model

This document defines the user roles for The Agent Command Center and their associated permissions.

## Roles

### 1. Public Viewer
- **Can view dashboard?**: Yes
- **Can call read-only status endpoints?**: Yes (publicly exposed ones)
- **Can view audit logs?**: No
- **Can request an action?**: No
- **Can approve an action?**: No
- **Can execute an action?**: No
- **Can manage secrets?**: No
- **Can merge/deploy/push?**: No

### 2. Operator
- **Can view dashboard?**: Yes
- **Can call read-only status endpoints?**: Yes
- **Can view audit logs?**: Yes (read-only)
- **Can request an action?**: Yes
- **Can approve an action?**: No
- **Can execute an action?**: No
- **Can manage secrets?**: No
- **Can merge/deploy/push?**: No

### 3. Admin
- **Can view dashboard?**: Yes
- **Can call read-only status endpoints?**: Yes
- **Can view audit logs?**: Yes
- **Can request an action?**: Yes
- **Can approve an action?**: Yes
- **Can execute an action?**: No (unless explicitly elevated)
- **Can manage secrets?**: No
- **Can merge/deploy/push?**: No

### 4. Auditor
- **Can view dashboard?**: Yes
- **Can call read-only status endpoints?**: Yes
- **Can view audit logs?**: Yes (full access)
- **Can request an action?**: No
- **Can approve an action?**: No
- **Can execute an action?**: No
- **Can manage secrets?**: No
- **Can merge/deploy/push?**: No

### 5. System Maintainer
- **Can view dashboard?**: Yes
- **Can call read-only status endpoints?**: Yes
- **Can view audit logs?**: Yes
- **Can request an action?**: Yes
- **Can approve an action?**: Yes
- **Can execute an action?**: Yes (controlled)
- **Can manage secrets?**: Yes (via platform UI)
- **Can merge/deploy/push?**: Yes (via Git)

## Default Policy
For all roles, the default permission for dangerous or system-altering capabilities is **NO**. Permissions are additive and must be explicitly defined in the API logic.

---
*Note: This is a planning document only. No functional implementation is included in this build.*

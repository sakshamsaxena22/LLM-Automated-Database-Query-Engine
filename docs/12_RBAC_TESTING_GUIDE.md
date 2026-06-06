# RBAC Testing Guide

This guide outlines exactly how to test the Role-Based Access Control (RBAC) system using the default accounts seeded in the database.

## Prerequisites
Ensure your database is seeded with the test accounts by running:
```bash
python backend/seed_data/seed_users.py
```

### The Test Accounts (Passwords are as defined in the seed script)
* `viewer@enterprise.com` (Role: Viewer)
* `editor@enterprise.com` (Role: Editor)
* `admin@enterprise.com` (Role: Admin)
* `superadmin@enterprise.com` (Role: Super Admin)

---

## Test 1: Read Access (Allowed for everyone)
1. **Log in** as `viewer@enterprise.com`.
2. Go to the **Query Console** and run: `"Show all users"` or `"Find 10 transactions"`.
3. **Expected Result:** **Success!** Viewers are allowed to execute safe `find` and `aggregate` queries.

## Test 2: Creating & Editing Data (Requires Editor+)
1. Still logged in as `viewer@enterprise.com`.
2. Go to the **Data Manager** page, try to "Add Record" or Edit an existing record.
3. **Expected Result:** **Blocked (403 Forbidden).** Viewers cannot modify data.
4. **Log out**, and log back in as `editor@enterprise.com`. Try to edit a record again.
5. **Expected Result:** **Success!** Editors are authorized to insert and update data.

## Test 3: Deleting Data (Requires Admin+)
1. Logged in as `editor@enterprise.com`.
2. Go to the **Data Manager**, select a record, and click **Delete**.
3. **Expected Result:** **Blocked (403 Forbidden).** Editors can create/edit, but they cannot destroy data.
4. **Log out**, and log back in as `admin@enterprise.com`. Try to delete the record again.
5. **Expected Result:** **Success!** Admins and Super Admins have destructive privileges.

## Test 4: System Administration (Requires Admin+)
1. Log in as `editor@enterprise.com`.
2. Try to navigate to the **User Management** or **Audit Logs** pages in the sidebar.
3. **Expected Result:** **Blocked (403 Forbidden).** You won't be able to fetch the user lists or audit trails.
4. **Log out**, and log back in as `admin@enterprise.com`.
5. **Expected Result:** **Success!** You can view the audit logs, see all registered users, and even change their roles!

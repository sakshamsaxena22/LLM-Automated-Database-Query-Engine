# Frontend Portal & Functionality Guide

This document explains the architecture of the frontend dashboard, detailing what each portal does, why it exists from a business/security perspective, and how it ties into the platform's overarching Role-Based Access Control (RBAC) system.

---

## 1. Query Console (AI Query)
**What it is:** The heart of the platform. A chat-like interface where users can type questions in plain English (e.g., "Find all pending transactions over $500") and instantly receive structured data tables in response.
**Why it exists:** 
* **Accessibility:** Allows non-technical users (sales, support, management) to query complex databases without knowing SQL or MongoDB aggregation pipelines.
* **Safety:** It translates natural language into an Intermediate Query Representation (IQR) that is strictly validated before execution. It prevents anyone from accidentally dropping a database or updating records through a chat interface.

## 2. Data Manager (CRUD Console)
**What it is:** A traditional spreadsheet-like view of the database collections allowing users to Add, Edit, or Delete raw JSON records directly.
**Why it exists:** 
* **Data Correction:** Sometimes automated systems or users make mistakes. Support agents or data entry clerks need a simple UI to correct typos, refund transactions, or update statuses manually without asking a developer to run a database script.
* **Direct Control:** While the AI is great for searching, structured data entry is often faster and safer when done through explicit, validated forms.

## 3. User Management
**What it is:** An administrative table showing all registered users, their emails, their active status, and a dropdown to change their roles.
**Why it exists:**
* **Security & Onboarding:** When a new employee joins the company, they register an account. By default, they are granted the lowest privilege (`Viewer`). An Admin must use this portal to upgrade them to `Editor` or `Manager` before they can modify data.
* **Offboarding:** When someone leaves the company, an Admin can instantly revoke their access by setting their account to "Inactive" or downgrading them, preventing data leaks.

## 4. Audit Logs
**What it is:** An immutable, chronological ledger recording every single action taken on the platform. It tracks *Who* (User ID), *What* (Operation like Insert/Delete), *Where* (Which collection), and *When* (Timestamp).
**Why it exists:**
* **Compliance:** Frameworks like SOC2, HIPAA, or GDPR require strict tracking of who accessed or modified user data. If a customer complains that their payment was deleted, the audit log proves exactly which employee deleted it and when.
* **Security Forensics:** If an account is compromised and starts mass-deleting records, the Audit Log triggers high-risk alerts and provides a trail to immediately identify the blast radius and restore the data.
* **Accountability:** Knowing that every action is permanently logged discourages employees from abusing their privileges (e.g., viewing data they shouldn't or covering up mistakes).

## 5. Analytics Overview
**What it is:** High-level charts and metrics summarizing the platform's usage (e.g., Total Queries, Total Users, Error Rates).
**Why it exists:**
* **Platform Health:** Helps the engineering and product teams understand how much load the system is under. If the number of failed queries spikes, it indicates the AI model might be struggling or a database connection is failing.
* **Billing/Quota Tracking:** If you are paying for LLM tokens (like Groq/OpenAI), tracking the total queries helps forecast operational costs.

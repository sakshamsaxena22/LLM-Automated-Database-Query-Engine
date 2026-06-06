# Troubleshooting & Error Resolution Log

This document records complex deployment and configuration errors encountered during the migration from local development to production (Render, Vercel, MongoDB Atlas) and how they were solved.

## 1. Frontend Page Refreshing on Login Error
**Issue:** 
When users entered an invalid email or password, the Vercel frontend would briefly flash an error and then instantly refresh the page, hiding the error message.
**Cause:** 
An Axios response interceptor in `client.ts` was configured to blindly catch all `401 Unauthorized` responses and redirect the user to `/login`. This is meant for expired tokens, but it was catching the `401` from a failed login attempt too.
**Resolution:** 
Added a condition in the interceptor to explicitly ignore `401` errors if the request URL contains `/auth/login` or `/auth/register`.

## 2. CORS Error on `/auth/register` (The "Fake" CORS Error)
**Issue:** 
Attempting to register an account from the frontend resulted in a browser console error: `Blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present`.
**Cause:** 
The backend was actually throwing a `500 Internal Server Error` under the hood. When FastAPI hits an unhandled exception before returning a response, it can fail to attach CORS headers, causing the browser to misinterpret the 500 error as a CORS policy violation.
**Resolution:** 
The underlying `500 Internal Server Error` was traced to a MongoDB Atlas configuration issue (see below).

## 3. MongoDB Atlas 500 Error (Wrong Database Name)
**Issue:** 
The backend successfully connected to the cluster but threw a 500 error when trying to insert a new user document.
**Cause:** 
The `DATABASE_NAME` environment variable on Render was accidentally set to `"automateddb"` (the name of the MongoDB cluster). The actual databases inside the cluster were named `enterprise_db` and `payments`. Because the Atlas user didn't have privileges to dynamically create a new database called `"automateddb"`, the `insert_one` operation crashed with an `OperationFailure`.
**Resolution:** 
Changed the `DATABASE_NAME` environment variable in the Render dashboard to `enterprise_db`. The backend automatically uses this default database for users and audit logs, and handles dynamic routing to the `payments` database via `MongoAdapter._collection()`.

## 4. "LLM did not return valid JSON" on AI Query
**Issue:** 
When users typed conversational text (e.g., "hello") into the AI Query console, the API returned a 400 Bad Request with the detail `"LLM did not return valid JSON"`.
**Cause:** 
The LLM is strictly instructed via its system prompt to ONLY return JSON database queries. If asked a conversational question, it replies in natural language ("I cannot answer that"). The backend's JSON extractor fails and throws a generic validation error.
**Resolution:** 
Updated `AIService.generate_query` to catch non-JSON outputs and return a much clearer, user-friendly error: `"Forbidden or invalid query: The AI cannot perform write/modification requests and requires a clear database question."`

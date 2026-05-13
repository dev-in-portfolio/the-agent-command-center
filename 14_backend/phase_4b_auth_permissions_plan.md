# Phase 4B: Authentication & Permissions Plan

## Overview
This document outlines the authentication and permissions strategy for The Agent Command Center. Adding these layers is a prerequisite for any future sensitive backend capabilities, such as action requests or command execution.

## Why Auth is Needed
Authentication ensures that only authorized personnel can access non-public data or request system-altering actions. Without it, the dashboard remains strictly read-only for public safety.

## Recommended Auth Options
- **Netlify Identity**: Leveraging the existing platform's native identity service for same-origin authentication.
- **Role-Based JWTs**: Using JSON Web Tokens to securely carry identity and permission data between the frontend and Netlify Functions.

## Architecture Considerations
- **Same-Origin Policy**: All auth-related requests must be same-origin to prevent CSRF and simplify session management.
- **Secure Sessions**: HTTP-only, Secure cookies should be used to store session tokens where possible.
- **Admin Boundary**: Distinct logical separation between public read-only views and authenticated operator/admin panels.

## What Phase 4B Does Not Implement
- No login UI or backend auth logic is added in this phase.
- No database integration is performed.
- No secrets are added to the environment.

## Decision Points before Phase 4C
- Select the primary identity provider (e.g., Netlify Identity vs. custom).
- Finalize the initial set of user roles and their mapping to GitHub teams if applicable.
- Define the secret management lifecycle for production.

---
*Note: This is a planning document only. No functional implementation is included in this build.*

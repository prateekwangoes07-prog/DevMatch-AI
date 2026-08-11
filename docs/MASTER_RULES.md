# Master Rules: DevMatch AI

These core rules govern the development, design, and architecture of DevMatch AI.

## Business & Allocation Rules
1. **Developer Workload Limit:** A developer can have a maximum of **2 active clients** at any given time.
2. **Authority:** The Backend is the sole authority for business rules. The Frontend is not a security or constraint enforcement layer. All restrictions must be verified on the backend.

## Integrations & Services
3. **Primary Database:** PostgreSQL 16 is the main application database and source of truth.
4. **Calendar & Meeting Booking:** Cal.com handles all direct client calls and schedules.
5. **Workload Visibility:** Google Sheets handles the visibility and synchronization of developer workloads and availability.

## Security & Operations
6. **Secrets Management:** Environment variables must always be used for secrets. Secrets, API keys, or database credentials must never be committed to git.
7. **Environment Separation:** Development and Production docker configurations must remain strictly separate. Do not use development bind mounts or hot reload configs in production.
8. **Keep It Simple:** Do not over-engineer. Focus on clean code, type safety, and direct solutions.

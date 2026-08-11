# Database Guide: DevMatch AI

PostgreSQL 16 serves as the primary system of record (main application database) for DevMatch AI.

## Database Role
All transactional data, developer records, client profiles, allocation logs, and admin accounts must be stored in PostgreSQL.

## Planned Key Entities (For Phase 2+)

1. **User / Admin Table**
   - User identity, credentials (hashed), role (Admin, Retail, Developer).

2. **Developer Table**
   - Name, skills (AI/ML, Automation, DevOps), email, active client count.

3. **Client / Contact Request Table**
   - Client name, organization, requirements text, identified developer role, status (Pending, Approved, Rejected).

4. **Allocation Table**
   - Active mappings matching a developer to a client.

## Workload Synchronization (Google Sheets)
While PostgreSQL holds the structural relational data, developer workload and availability status will be synced to Google Sheets for high visibility and manual overrides by non-technical management.

# Architecture Guide: DevMatch AI

This document provides a high-level view of the DevMatch AI communication and data architecture.

## System Flow Diagram

```mermaid
graph TD
    Customer([Customer / Client])
    
    %% Ingestion Channels
    Customer -->|Voice Call / SMS| TwilioRetell[Twilio + Retell AI Voice Agent]
    Customer -->|WhatsApp Message| WhatsAppAPI[WhatsApp Business API]
    Customer -->|Email Inquiry| EmailService[Email Service]
    
    %% Core Processing Layer
    TwilioRetell -->|Analyze & Extract Requirements| AIAgent[AI Agent Layer]
    WhatsAppAPI -->|Parse Text| AIAgent
    EmailService -->|Parse Body| AIAgent
    
    %% API & Backend Layer
    AIAgent -->|Submit Request / Structured JSON| FastAPI[FastAPI Backend]
    
    %% Integration & Storage Layer
    FastAPI -->|Write Allocations / User Data| PostgreSQL[(PostgreSQL Database)]
    FastAPI -->|Schedule Client Bookings| Cal[Cal.com Integration]
    FastAPI -->|Sync Workloads & Rosters| GoogleSheets[Google Sheets Integration]
    
    %% Admin Interface
    FastAPI <-->|JSON REST API / Cookies Auth| NextJS[Next.js Admin & Retail Dashboard]
    NextJS <-->|Approve/Reject Requests| Admin([Retail / Admin User])
```

## Architectural Components

1. **Client Intake Channels:** Multi-modal intake (Voice via Retell, SMS/WhatsApp, Email) handles incoming customer inquiries.
2. **AI Processing Agent:** Interprets customer requests to identify target skills (AI/ML, DevOps, Automation) and developer profiles.
3. **Backend Service (FastAPI):** Central business logic engine enforcing client limits (max 2 active clients per developer) and security.
4. **Data & Synchronization Layer:**
   - **PostgreSQL 16:** Main source of truth database.
   - **Google Sheets:** Read/write developer availability mapping.
   - **Cal.com:** External scheduler for calls.
5. **Dashboard Interface (Next.js):** Provides a visual management tool for admin staff to oversee allocation recommendations, manually override, and manage settings.

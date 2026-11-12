# Enterprise Incident & Support Operations Engine (ISO-Engine)

An autonomous, production-grade incident ingestion, PII sanitization, extraction, routing, and SLA escalation engine built with **FastAPI**, **OpenAI API**, **Pydantic**, and native **SQLite**. 

Designed for enterprise reliability, the engine parses unstructured operational alerts, classifies severity and categories using structured LLM outputs, enforces deterministic routing and SLA escalation policies, and persists immutable audit trails.

---

## 🏗️ System Architecture

The pipeline processes incoming tickets through a deterministic, multi-stage pipeline:

```mermaid
graph TD
    A["Raw Incident Text"] --> B["PII Sanitizer & Extractor"]
    B --> C["LLM Structured Extractor (Pydantic)"]
    C --> D["Deterministic Policy & SLA Engine"]
    D --> E{"Urgency == CRITICAL?"}
    E -- Yes --> F["Automatic Escalation & PagerDuty Page"]
    E -- No --> G["Standard Team Routing & Webhook Dispatch"]
    F --> H[("SQLite Persistence: tickets & audit_logs")]
    G --> H
    H --> I["Observability Metrics Endpoint"]
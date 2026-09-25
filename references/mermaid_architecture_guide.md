# Mermaid Architecture & Diagramming Standards

This guide enforces syntax invariants for rendering rock-solid Mermaid diagrams in generated documentation.

---

## 1. Graph & Architecture Best Practices

### Node IDs and Special Characters
Always wrap node labels in double quotes if they contain spaces, parentheses, slashes, or special characters:
```mermaid
graph TB
    %% CORRECT
    auth_service["Authentication Service (v2.1)"]
    db_node[("PostgreSQL 16 Primary")]
    
    auth_service -->|JSON / HTTPS| db_node
```

### Subgraph Boundaries
Organize components by architectural layers:
```mermaid
graph TB
    subgraph ClientTier ["Frontend & Client Layer"]
        web_app["Web SPA (Next.js)"]
        mobile_app["Mobile App (Flutter)"]
    end

    subgraph IngressTier ["Ingress & Gateway"]
        traefik["Traefik Reverse Proxy"]
    end

    subgraph ServiceTier ["Domain Microservices"]
        auth["Auth Service"]
        order["Order Service"]
        payment["Payment Gateway"]
    end

    subgraph DataTier ["Persistence Tier"]
        pg[(PostgreSQL)]
        redis[(Redis Cache)]
    end

    web_app --> traefik
    mobile_app --> traefik
    traefik --> auth
    traefik --> order
    traefik --> payment
    auth --> pg
    order --> pg
    payment --> redis
```

---

## 2. Sequence Diagrams

Always enable `autonumber` and quote actor/participant labels:
```mermaid
sequenceDiagram
    autonumber
    actor Client as "Web / API Consumer"
    participant Gateway as "API Gateway"
    participant Service as "Payment Service"
    participant DB as "PostgreSQL DB"

    Client->>Gateway: POST /api/v1/charge (Payload)
    Gateway->>Gateway: Verify Bearer JWT
    Gateway->>Service: Forward Authenticated Request
    Service->>DB: Check Idempotency Key
    alt Key Exists
        DB-->>Service: Return Existing Transaction
        Service-->>Client: HTTP 200 (Cached Result)
    else Key Is New
        Service->>DB: Insert Pending Transaction
        Service-->>Client: HTTP 201 Created
    end
```

---

## 3. Entity-Relationship Diagrams (ERD)

Use standard Crow's Foot notation:
```mermaid
erDiagram
    TENANT ||--o{ USER : owns
    USER ||--o{ API_KEY : generates
    USER ||--o{ AUDIT_LOG : triggers

    TENANT {
        uuid id PK
        string name
        string plan
        timestamp created_at
    }
    USER {
        uuid id PK
        uuid tenant_id FK
        string email UK
        string password_hash
        string status
    }
```

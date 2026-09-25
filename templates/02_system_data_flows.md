# [Project Name] — System Data Flows, State Machines & Pipelines

> **Document ID**: `02_SYSTEM_DATA_FLOWS`  
> **Classification**: Dynamic Interaction & Lifecycle Specifications  
> **Purpose**: Documents all asynchronous flows, state transitions, event publishers/subscribers, and data pipelines.

---

## 1. Global State Transition Diagrams

### [Entity / Lifecycle State Machine, e.g., Order / Job / User Lifecycle]
```mermaid
stateDiagram-v2
    [*] --> Draft : Created
    Draft --> PendingValidation : Submit
    PendingValidation --> Active : Validation Passed
    PendingValidation --> Rejected : Validation Failed
    Active --> Processing : Trigger Worker
    Processing --> Completed : Success
    Processing --> Failed : Fatal Error
    Failed --> Retrying : Retry Policy Triggered
    Retrying --> Processing
    Completed --> [*]
    Rejected --> [*]
```

---

## 2. Event-Driven & Asynchronous Data Pipelines

### Event Bus / Queue Topology
- **Message Broker**: [e.g. Redis Pub/Sub, RabbitMQ, Kafka, AWS SQS]
- **Dead Letter Queue (DLQ) Strategy**: [Retry counts, backoff multipliers, alert routing]

```mermaid
sequenceDiagram
    autonumber
    participant Producer as API / Producer
    participant Broker as Message Broker
    participant Consumer as Worker Daemon
    participant Ext as Third-Party API

    Producer->>Broker: Publish Event: `order.created` (Payload)
    Broker-->>Consumer: Pull / Push Message to Consumer Group
    Consumer->>Consumer: Validate Schema & Idempotency Key
    Consumer->>Ext: Dispatch Webhook / Notification
    alt Processing Succeeded
        Consumer->>Broker: ACK (Acknowledge Message)
    else Transient Failure
        Consumer->>Broker: NACK (Requeue with Exponential Backoff)
    else Poison Pill / Max Retries
        Consumer->>Broker: Route to Dead Letter Queue (DLQ)
    end
```

---

## 3. Real-Time & Streaming Protocols (WebSockets / SSE / gRPC)

- **Connection Handshake**: [Auth tokens, query headers, protocol negotiation]
- **Heartbeat & Keep-Alive**: [Ping-pong interval, timeout threshold]
- **Channel / Topic Multiplexing**: [Subscribed topics, message formats]

---

## 4. Cache & Synchronization Strategy

- **Cache Layer**: [Redis, Memcached, Local LRU]
- **Eviction / Invalidation Policy**: [Cache-aside, Write-through, TTL values, Tag invalidation]
- **Race Condition Mitigations**: [Distributed locking via Redlock, optimistic concurrency control]

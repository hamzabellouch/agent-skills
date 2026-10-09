---
name: omnichannel-helpdesk-ticket-routing
metadata:
  category: Customer Support and Service Automation
description: Architect automated omnichannel helpdesk routing and SLA lifecycle engines across email, chat, SMS, and webhooks. Integrate with ticketing systems (Zendesk, Freshdesk, Jira Service Management), enforce strict SLA tier policies (response time, resolution time), implement skill-based agent routing, and manage ticket state machines. Trigger when building customer service backends, routing algorithms, or support automation systems.
compatibility: REST Webhooks, Zendesk v2 API, Freshdesk v2 API
---

# Omnichannel Helpdesk & Ticket Routing Skill Guide

This skill provides architectural patterns, state machine designs, and automated routing logic for high-volume customer support operations.

---

## 1. Ticket Lifecycle & Routing State Machine

```text
[ Incoming Ingestion ] (Email / Chat / WhatsApp / Webhook)
             |
             v
[ Normalization & Deduplication Layer ]
             |
             v
[ Ticket Classifier & SLA Policy Attacher ]
  |-- Calculate Response SLA (e.g., P1 = 15m, P2 = 1h, P3 = 4h)
  |-- Tag Tier: VIP / Standard
             |
             v
[ Skill-Based Routing Engine ]
  |-- Match Agent Language, Product Domain, and Shift Status
  |-- Distribute via Round-Robin or Least-Loaded Capacity
             |
             v
[ Assigned to Agent / Auto-Resolved via AI Assistant ]
```

---

## 2. Production Code Implementations

### A. Skill-Based Round-Robin Routing Engine (Python)

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import heapq


class Priority(Enum):
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Agent:
    id: str
    name: str
    skills: set[str]
    active_ticket_count: int = 0
    max_capacity: int = 5
    is_online: bool = True

    def is_eligible(self, required_skills: set[str]) -> bool:
        return self.is_online and (self.active_ticket_count < self.max_capacity) and required_skills.issubset(self.skills)


@dataclass
class Ticket:
    id: str
    priority: Priority
    required_skills: set[str]
    customer_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_agent_id: str | None = None


class TicketRouter:
    def __init__(self, agents: list[Agent]):
        self.agents = agents

    def route_ticket(self, ticket: Ticket) -> Agent | None:
        """Finds eligible agent with minimum active ticket count (Least-Loaded)."""
        eligible_agents = [
            agent for agent in self.agents
            if agent.is_eligible(ticket.required_skills)
        ]

        if not eligible_agents:
            return None  # Enqueue to backlog / fallback queue

        # Sort by active tickets ascending
        selected_agent = min(eligible_agents, key=lambda a: a.active_ticket_count)
        selected_agent.active_ticket_count += 1
        ticket.assigned_agent_id = selected_agent.id
        return selected_agent
```

### B. SLA Breach Warning & Webhook Monitor (TypeScript / Node.js)

```typescript
export interface SLAPolicy {
  p1MaxResponseMinutes: number; // e.g. 15
  p2MaxResponseMinutes: number; // e.g. 60
  p3MaxResponseMinutes: number; // e.g. 240
}

export function evaluateSLABreach(
  ticketPriority: "P1" | "P2" | "P3",
  createdAtIso: string,
  firstResponseAtIso: string | null,
  policy: SLAPolicy
): { isBreached: boolean; minutesRemaining: number } {
  const created = new Date(createdAtIso).getTime();
  const now = Date.now();
  const elapsedMinutes = (now - created) / (1000 * 60);

  const limitMinutes =
    ticketPriority === "P1"
      ? policy.p1MaxResponseMinutes
      : ticketPriority === "P2"
      ? policy.p2MaxResponseMinutes
      : policy.p3MaxResponseMinutes;

  if (firstResponseAtIso) {
    const respondedTime = (new Date(firstResponseAtIso).getTime() - created) / (1000 * 60);
    return { isBreached: respondedTime > limitMinutes, minutesRemaining: 0 };
  }

  const minutesRemaining = limitMinutes - elapsedMinutes;
  return {
    isBreached: minutesRemaining <= 0,
    minutesRemaining: Math.round(minutesRemaining),
  };
}
```

---

## 3. Best Practices Checklist

- [ ] **Deduplication:** Generate a deterministic message hash of (customer_id, normalized_subject, last_message_body) within a 5-minute sliding window to prevent duplicate tickets from webhook flurries.
- [ ] **Graceful Degraded Routing:** If no agent matching required skills is available, escalate to a generic Senior Tier 1 triage group rather than stalling in limbo.
- [ ] **SLA Pause Conditions:** Automatically pause SLA countdown clocks when ticket status moves to "Pending Customer Information".

---
name: csat-sentiment-triage-automation
metadata:
  category: Customer Support and Service Automation
description: Automate customer service ticket sentiment analysis, churn risk detection, and intelligent escalation using LLM embeddings and classification pipelines. Extract customer emotional valence, urgency scores, dissatisfaction root causes, and trigger automated manager escalations or CSAT recovery playbooks. Trigger when building sentiment triage, churn prevention, or automated customer support feedback loops.
compatibility: Python 3.10+, OpenAI / Anthropic / Gemini API, HuggingFace Transformers
---

# CSAT & Sentiment Triage Automation Skill Guide

This skill governs the integration of machine learning and LLM-driven sentiment evaluation to prioritize frustrated customers, flag churn indicators, and trigger automated escalations.

---

## 1. Sentiment & Churn Triage Architecture

```text
[ Incoming Customer Message / Survey ]
                  |
                  v
[ Fast Sentiment & Intent Classifier ]
  |-- Valence: Negative / Neutral / Positive
  |-- Urgency Score (1 - 10)
  |-- Churn Risk Triggers: "cancel", "refund", "unacceptable", "lawyer"
                  |
                  +---> High Urgency / Severe Negative (Score >= 8)
                  |       |
                  |       v
                  |     [ Immediate Manager Slack Alert & P1 Queue Boost ]
                  |
                  +---> Mild / Standard Query
                          |
                          v
                        [ Normal Agent Assignment / AI Auto-Draft ]
```

---

## 2. Production Implementation (Python & Pydantic)

```python
import json
from typing import Literal
from pydantic import BaseModel, Field


class SentimentTriageResult(BaseModel):
    sentiment: Literal["VERY_NEGATIVE", "NEGATIVE", "NEUTRAL", "POSITIVE"]
    urgency_score: int = Field(ge=1, le=10, description="1=low, 10=immediate crisis")
    churn_risk: bool
    detected_issues: list[str]
    suggested_action: Literal["ESCALATE_TO_MANAGER", "PRIORITY_SUPPORT", "STANDARD_QUEUE", "OFFER_RETENTION"]
    executive_summary: str


def build_triage_prompt(customer_message: str, account_tier: str) -> str:
    return f"""You are an expert customer experience triage intelligence agent.
Analyze the following customer message and account context:

Customer Account Tier: {account_tier}
Message Content:
\"\"\"{customer_message}\"\"\"

Provide an objective assessment in JSON matching the schema:
- sentiment: VERY_NEGATIVE | NEGATIVE | NEUTRAL | POSITIVE
- urgency_score: 1 to 10
- churn_risk: true if the customer expresses intent to leave, cancel, or switch competitors
- detected_issues: list of core issues (e.g., "downtime", "billing error", "rude support")
- suggested_action: ESCALATE_TO_MANAGER | PRIORITY_SUPPORT | STANDARD_QUEUE | OFFER_RETENTION
- executive_summary: 1-sentence summary for the receiving agent
"""


def process_sentiment_webhook(triage_data: SentimentTriageResult, ticket_id: str):
    """Executes action based on structured sentiment classification."""
    if triage_data.urgency_score >= 8 or triage_data.churn_risk:
        # Boost ticket priority and notify escalation Slack channel
        print(f"[URGENT ESCALATION] Ticket {ticket_id}: {triage_data.executive_summary}")
        # Integration logic: emit webhook / update CRM
```

---

## 3. Best Practices & Guardrails

1. **VIP Bias Adjustment:** Automatically add +2 to urgency score for enterprise/VIP contract accounts to ensure SLA compliance.
2. **Defamation & Legal Watchwords:** Configure zero-latency regex filters for keywords like "attorney", "subpoena", or "regulator" to route directly to legal/compliance queues.
3. **Continuous CSAT Closed-Loop:** When a customer rates a resolved ticket 1 or 2 stars, trigger an automatic follow-up ticket assigned to an operations team lead.

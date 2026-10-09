---
name: rest-openapi-spec-design
metadata:
  category: APIs and Integration Design
description: Production-grade RESTful API design standards, OpenAPI 3.1 specification structuring, contract-first API development, versioning strategies, rate limiting, and schema validation.
compatibility: OpenAPI 3.0/3.1, Swagger UI, Redoc, Prism Mock Server, Node.js / Python / Go
---

# RESTful API & OpenAPI 3.1 Specification Design

## Overview
This skill provides comprehensive standards and operational patterns for designing contract-first RESTful APIs using the **OpenAPI 3.1 Specification (OAS 3.1)**. It covers clean schema definitions, reusable `$ref` components, pagination, rate limiting headers, idempotency keys, error contracts (RFC 7807), and automated mock server validation.

---

## 1. Contract-First API Design Principles

1. **Contract-First Workflow**: Define the OpenAPI 3.1 schema before writing backend code. Validate requests and responses strictly against the OAS spec using middleware.
2. **Resource-Oriented Nouns**: Use plural nouns for resource endpoints (`/v1/orders`, `/v1/users/{userId}/invoices`). Avoid verbs in URI paths (use `POST /v1/orders/{id}/cancel` only for RPC-style actions when RESTful state update is unsuitable).
3. **HTTP Method Semantics**:
   - `GET`: Idempotent & safe resource retrieval.
   - `POST`: Non-idempotent resource creation or action execution.
   - `PUT`: Idempotent resource replacement (requires full body).
   - `PATCH`: Idempotent partial resource update (JSON Patch RFC 6902 or JSON Merge Patch RFC 7396).
   - `DELETE`: Idempotent resource removal.
4. **Standardized Error Handling (RFC 7807)**: All API errors must return `application/problem+json` formatted responses containing `type`, `title`, `status`, `detail`, and `instance`.
5. **API Versioning**: Enforce explicit semantic versioning in the URL path (`/v1/`, `/v2/`) or content negotiation via custom Accept headers (`Accept: application/vnd.company.v1+json`).

---

## 2. API Architecture & Standard Headers

```
[ Client Application ]
       │
       │ 1. Request with Bearer Token & Idempotency-Key
       ▼
[ API Gateway / Reverse Proxy ] ──(Rate Limit Check: X-RateLimit-*)
       │
       │ 2. Validate Request against OpenAPI Spec
       ▼
[ Microservice Backend ] ──(RFC 7807 Problem Detail on Failure)
```

| Standard Header | Direction | Purpose | Example Value |
| :--- | :--- | :--- | :--- |
| `Authorization` | Request | Bearer JWT / API Key authentication | `Bearer eyJhbGciOiJKV1Qi...` |
| `Idempotency-Key` | Request | Guarantee safe retry execution for `POST` actions | `7b9e1d2c-8a4f-4e3b-9c2d-1a0e9f8c7b6a` |
| `X-RateLimit-Limit` | Response | Max requests permitted in current window | `1000` |
| `X-RateLimit-Remaining` | Response | Remaining quota in active window | `984` |
| `X-RateLimit-Reset` | Response | UTC Epoch seconds when quota resets | `1770000000` |
| `Content-Type` | Both | Media type payload indicator | `application/json` / `application/problem+json` |

---

## 3. Anti-Patterns & Common Errors

* **Anti-Pattern: Status Code 200 OK with Internal Error Payload (`{"success": false, "error": "Unauthorized"}`)**
  * *Risk*: Breaks HTTP client retry logic, monitoring alerts, and API gateway routing.
  * *Remediation*: Return explicit HTTP status codes (401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity).
* **Anti-Pattern: Monolithic OpenAPI Files (10,000+ lines)**
  * *Risk*: Impossible code reviews, high merge conflict frequency, poor tooling performance.
  * *Remediation*: Modularize schemas using multi-file `$ref` structures and aggregate via Redocly CLI or Swagger CLI (`redocly bundle`).
* **Anti-Pattern: Unbounded List Responses**
  * *Risk*: Database memory exhaustion, excessive network latency on large datasets.
  * *Remediation*: Enforce cursor-based or limit-offset pagination with mandatory default limit (`limit=20`, `max_limit=100`).

---

## 4. Production OpenAPI 3.1 & Validation Snippets

### A. Modular OpenAPI 3.1 Specification (`openapi.yaml`)

```yaml
openapi: 3.1.0
info:
  title: Enterprise Order Management API
  description: High-performance, contract-first API for order lifecycle processing.
  version: 1.2.0
  contact:
    name: API Engineering Team
    email: api-team@enterprise.com

servers:
  - url: https://api.enterprise.com/v1
    description: Production Environment
  - url: https://sandbox-api.enterprise.com/v1
    description: Staging / Sandbox Environment

paths:
  /orders:
    post:
      summary: Create a new order
      operationId: createOrder
      tags:
        - Orders
      security:
        - OAuth2Bearer:
            - orders:write
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
          description: Unique UUID v4 key to prevent duplicate order processing.
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Order successfully created.
          headers:
            Location:
              description: URI of created order resource.
              schema:
                type: string
                format: uri
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
        '400':
          $ref: '#/components/responses/BadRequestProblem'
        '409':
          $ref: '#/components/responses/ConflictProblem'
        '422':
          $ref: '#/components/responses/UnprocessableEntityProblem'

  /orders/{orderId}:
    get:
      summary: Retrieve order by ID
      operationId: getOrderById
      tags:
        - Orders
      security:
        - OAuth2Bearer:
            - orders:read
      parameters:
        - name: orderId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Order retrieved successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
        '404':
          $ref: '#/components/responses/NotFoundProblem'

components:
  securitySchemes:
    OAuth2Bearer:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    CreateOrderRequest:
      type: object
      required:
        - customerId
        - items
        - currency
      properties:
        customerId:
          type: string
          format: uuid
        currency:
          type: string
          enum: [USD, EUR, GBP]
        items:
          type: array
          minItems: 1
          items:
            $ref: '#/components/schemas/OrderItem'

    OrderItem:
      type: object
      required:
        - productId
        - quantity
        - unitPrice
      properties:
        productId:
          type: string
          format: uuid
        quantity:
          type: integer
          minimum: 1
        unitPrice:
          type: number
          multipleOf: 0.01

    OrderResponse:
      type: object
      required:
        - id
        - customerId
        - status
        - totalAmount
        - createdAt
      properties:
        id:
          type: string
          format: uuid
        customerId:
          type: string
          format: uuid
        status:
          type: string
          enum: [PENDING, PROCESSING, COMPLETED, CANCELLED]
        totalAmount:
          type: number
        createdAt:
          type: string
          format: date-time

    ProblemDetails:
      type: object
      required:
        - type
        - title
        - status
        - detail
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri

  responses:
    BadRequestProblem:
      description: Bad Request (RFC 7807)
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
    NotFoundProblem:
      description: Resource Not Found (RFC 7807)
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
    ConflictProblem:
      description: Resource Conflict / Duplicate Request (RFC 7807)
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
    UnprocessableEntityProblem:
      description: Validation Failed (RFC 7807)
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
```

---

### B. Node.js Express Middleware Validation via OpenAPI Spec (`server.js`)

```javascript
import express from 'express';
import * as OpenApiValidator from 'express-openapi-validator';
import path from 'path';

const app = express();
app.use(express.json());

// Enforce OpenAPI Request & Response Validation Middleware
app.use(
  OpenApiValidator.middleware({
    apiSpec: './openapi.yaml',
    validateRequests: true,
    validateResponses: true,
    ignorePaths: /^\/docs/
  })
);

// Router implementation matching OpenAPI operationId
app.post('/v1/orders', (req, res) => {
  const idempotencyKey = req.headers['idempotency-key'];
  const { customerId, items, currency } = req.body;

  const totalAmount = items.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0);

  const newOrder = {
    id: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    customerId,
    status: 'PENDING',
    totalAmount: Number(totalAmount.toFixed(2)),
    createdAt: new Date().toISOString()
  };

  res.setHeader('Location', `/v1/orders/${newOrder.id}`);
  return res.status(201).json(newOrder);
});

// Centralized RFC 7807 Error Handler
app.use((err, req, res, next) => {
  const status = err.status || 500;
  res.status(status).type('application/problem+json').json({
    type: `https://api.enterprise.com/errors/${err.name || 'internal-error'}`,
    title: err.message || 'An internal server error occurred.',
    status: status,
    detail: err.errors ? JSON.stringify(err.errors) : err.message,
    instance: req.originalUrl
  });
});

app.listen(8080, () => console.log('API running on http://localhost:8080'));
```

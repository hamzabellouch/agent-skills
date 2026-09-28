---
name: spring-boot-production-architecture
metadata:
  category: Backend Frameworks and Runtimes
description: Production-grade Spring Boot 3.3+ architecture with Java 21, Project Loom virtual threads, layered architecture (Controller, Service, Repository, DTO), Spring Data JPA, connection pooling with HikariCP, transactional integrity, RFC 7807 ProblemDetails exception handling, and Micrometer observability. Trigger when building enterprise Java microservices or refactoring Spring Boot architectures.
compatibility: Spring Boot 3.2+, Java 21 LTS, Gradle 8+ / Maven 3.9+
---

# Spring Boot Production Architecture Skill Guide

This skill provides architectural patterns, production configurations, and idiomatic Java 21 code standards for building enterprise-grade, high-throughput microservices using Spring Boot 3.3+.

---

## 1. Architectural Layers & Virtual Thread Concurrency

Modern Spring Boot 3 applications leverage **Java 21 Virtual Threads (Project Loom)** to achieve non-blocking concurrency without reactive boilerplate.

```text
+------------------------------------------------------------------------+
| Client Request (HTTP / REST)                                           |
+------------------------------------------------------------------------+
                               |
                               v (Virtual Thread per Request)
+------------------------------------------------------------------------+
| Web Layer: @RestController                                              |
| - Request validation (@Valid, JSR-380)                                 |
| - DTO Mapping (MapStruct)                                              |
| - HTTP Status & RFC 7807 ProblemDetails Responses                     |
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| Domain / Service Layer: @Service                                       |
| - Business logic & Domain Invariants                                   |
| - Explicit Transaction Boundaries (@Transactional(readOnly = ...))    |
| - Event Publishing (ApplicationEventPublisher)                         |
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| Persistence Layer: @Repository                                         |
| - Spring Data JPA Repositories (Derived & JPQL Queries)                |
| - HikariCP Optimized Connection Pool                                   |
| - Database Migration (Flyway / Liquibase)                              |
+------------------------------------------------------------------------+
```

---

## 2. Core Production Implementation

### A. Application Configuration (`application.yml`)

```yaml
server:
  port: 8080
  shutdown: graceful
  tomcat:
    threads:
      max: 200
  compression:
    enabled: true
    mime-types: application/json,text/html,text/plain

spring:
  threads:
    virtual:
      enabled: true # Enable Java 21 Virtual Threads for all Web & Async tasks
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:orders_db}
    username: ${DB_USER:postgres}
    password: ${DB_PASS:secret}
    hikari:
      pool-name: SpringBootHikariPool
      maximum-pool-size: 20
      minimum-idle: 10
      idle-timeout: 300000
      connection-timeout: 20000
      max-lifetime: 1200000
  jpa:
    open-in-view: false # CRITICAL: Disable OSIV to prevent connection leaks
    hibernate:
      ddl-auto: validate # Schema validation only; migrations handled by Flyway
    properties:
      hibernate:
        format_sql: false
        jdbc.batch_size: 50
        order_inserts: true
        order_updates: true

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
```

### B. Clean Layered Domain Implementation

```java
package com.example.orders.domain;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "orders", indexes = {
    @Index(name = "idx_orders_customer_id", columnList = "customer_id"),
    @Index(name = "idx_orders_status", columnList = "status")
})
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "customer_id", nullable = false)
    private UUID customerId;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 32)
    private OrderStatus status;

    @Column(name = "total_amount", nullable = false, precision = 12, scale = 2)
    private BigDecimal totalAmount;

    @Version
    private Long version; // Optimistic locking

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = Instant.now();
        if (this.status == null) {
            this.status = OrderStatus.PENDING;
        }
    }
}
```

### C. Service with Strict Transactional Boundaries

```java
package com.example.orders.service;

import com.example.orders.domain.Order;
import com.example.orders.domain.OrderStatus;
import com.example.orders.dto.CreateOrderRequest;
import com.example.orders.dto.OrderResponse;
import com.example.orders.exception.ResourceNotFoundException;
import com.example.orders.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;

    @Transactional(readOnly = true)
    public OrderResponse getOrderById(UUID id) {
        return orderRepository.findById(id)
            .map(this::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("Order with ID " + id + " not found"));
    }

    @Transactional
    public OrderResponse createOrder(CreateOrderRequest request) {
        log.info("Creating new order for customer: {}", request.customerId());
        Order order = Order.builder()
            .customerId(request.customerId())
            .totalAmount(request.totalAmount())
            .status(OrderStatus.PENDING)
            .build();

        Order saved = orderRepository.save(order);
        return toResponse(saved);
    }

    private OrderResponse toResponse(Order order) {
        return new OrderResponse(
            order.getId(),
            order.getCustomerId(),
            order.getStatus(),
            order.getTotalAmount(),
            order.getCreatedAt()
        );
    }
}
```

### D. Global RFC 7807 ProblemDetails Exception Handler

```java
package com.example.orders.exception;

import org.springframework.http.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.net.URI;
import java.time.Instant;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleResourceNotFound(ResourceNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Resource Not Found");
        problem.setType(URI.create("https://api.example.com/errors/not-found"));
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidationErrors(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .collect(Collectors.joining(", "));

        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        problem.setTitle("Validation Failure");
        problem.setType(URI.create("https://api.example.com/errors/validation"));
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }
}
```

---

## 3. Production Best Practices & Quality Gates

1. **Virtual Threads Enabled:** Ensure `spring.threads.virtual.enabled: true` is active for high-concurrency throughput without Netty reactive overhead.
2. **Disable OSIV:** Always set `spring.jpa.open-in-view: false` to avoid holding database connections during template rendering or external serialization.
3. **Optimistic Locking:** Include `@Version private Long version;` on mutable entities to prevent concurrent write loss.
4. **Read-Only Transactions:** Enforce `@Transactional(readOnly = true)` on query methods to allow Hibernate to skip dirty checks and route to replica databases.

---
name: grpc-protobuf-microservices
metadata:
  category: APIs and Integration Design
description: High-performance gRPC microservices architecture, Protocol Buffers (proto3) schema design, streaming patterns, client/server interceptors, load balancing, and deadline propagation.
compatibility: Protocol Buffers v3, gRPC Go / Java / Node.js / Python, Envoy Proxy
---

# gRPC & Protocol Buffers Microservices Architecture

## Overview
This skill provides production-grade standards for designing, implementing, and deploying high-performance microservices using **gRPC** and **Protocol Buffers (proto3)**. It covers backward-compatible `.proto` schema evolution, unary and streaming RPC patterns, context deadline propagation, interceptor chains (middleware), and load balancing with Envoy.

---

## 1. Proto3 Schema & gRPC Core Principles

1. **Strict Backward Compatibility**: Never alter existing field tags (numbers). Never change field types. Use `reserved` statements when deleting fields to prevent tag reuse.
2. **Explicit Deadlines & Timeouts**: Every gRPC client call must specify an explicit context deadline to prevent cascading hangs across microservices.
3. **Structured Error Handling**: Use `google.rpc.Status` with rich error details (`BadRequest`, `PreconditionFailure`, `ResourceInfo`) rather than simple gRPC status codes.
4. **Streaming Semantics**:
   - **Unary**: Standard Request/Response pattern.
   - **Server Streaming**: Continuous feed (e.g., real-time audit logs, telemetry).
   - **Client Streaming**: Large file or batch data ingestion.
   - **Bi-directional Streaming**: Low-latency interactive chat or real-time state synchronization.
5. **Transport Security (mTLS)**: Enforce mutual TLS authentication between internal microservices.

---

## 2. Microservice Communication Architecture

```
[ Client / Web App ]
       │  HTTP/2 or gRPC-Web
       ▼
[ Envoy Reverse Proxy ] ──(gRPC Transcoding / Load Balancing)
       │  gRPC over HTTP/2 (mTLS)
       ├──▶ [ Order Service (gRPC Server) ]
       └──▶ [ Inventory Service (gRPC Server) ]
```

| RPC Pattern | Protocol Transport | Primary Use Case | Recommended Timeout |
| :--- | :--- | :--- | :--- |
| **Unary RPC** | HTTP/2 Single Frame | Transactional CRUD Operations | 500ms - 2s |
| **Server Streaming** | HTTP/2 Multi-Frame | Telemetry, Event Push, Activity Feeds | 15m - 1h (with keepalive) |
| **Client Streaming** | HTTP/2 Multi-Frame | Chunked File Upload, Batch Log Ingestion | 30s - 5m |
| **Bi-directional** | HTTP/2 Multiplexed | Live Synchronization, Streaming AI Inference | Continuous |

---

## 3. Anti-Patterns & Common Failures

* **Anti-Pattern: Reusing Field Numbers in Protocol Buffers**
  * *Risk*: Silent data corruption across distributed services during deployment.
  * *Remediation*: Always mark deleted fields with `reserved 4, 8 to 12;` and `reserved "old_field_name";`.
* **Anti-Pattern: Omitting Context Deadlines**
  * *Risk*: Resource exhaustion when downstream services stall, leading to thread pool starvation.
  * *Remediation*: Enforce global deadline interceptors on all client stubs (`context.WithTimeout`).
* **Anti-Pattern: Transmitting Large Arrays as Primitive Lists without Pagination**
  * *Risk*: Exceeding gRPC default max message payload size (4MB limit).
  * *Remediation*: Implement field masking (`google.protobuf.FieldMask`) and streaming pagination.

---

## 4. Production Protobuf Schema & Go Microservice

### A. Protocol Buffer Schema (`order_service.proto`)

```protobuf
syntax = "proto3";

package enterprise.orders.v1;

option go_package = "github.com/enterprise/orders/v1;ordersv1";

import "google/protobuf/timestamp.proto";
import "google/protobuf/field_mask.proto";

service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
  rpc GetOrder (GetOrderRequest) returns (OrderResponse);
  rpc StreamOrderUpdates (StreamOrderUpdatesRequest) returns (stream OrderStatusUpdate);
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_PROCESSING = 2;
  ORDER_STATUS_COMPLETED = 3;
  ORDER_STATUS_CANCELLED = 4;
}

message OrderItem {
  string product_id = 1;
  int32 quantity = 2;
  int64 unit_price_cents = 3;
}

message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
  string currency_code = 3;
  
  // Reserved for safe backward-compatible field deprecation
  reserved 4, 10 to 15;
  reserved "discount_code";
}

message GetOrderRequest {
  string order_id = 1;
  google.protobuf.FieldMask read_mask = 2;
}

message OrderResponse {
  string order_id = 1;
  string customer_id = 2;
  OrderStatus status = 3;
  int64 total_amount_cents = 4;
  google.protobuf.Timestamp created_at = 5;
}

message StreamOrderUpdatesRequest {
  string customer_id = 1;
}

message OrderStatusUpdate {
  string order_id = 1;
  OrderStatus status = 2;
  string status_message = 3;
  google.protobuf.Timestamp updated_at = 4;
}
```

---

### B. Production Go gRPC Server Implementation (`server.go`)

```go
package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"

	pb "github.com/enterprise/orders/v1"
)

type server struct {
	pb.UnimplementedOrderServiceServer
}

func (s *server) CreateOrder(ctx context.Context, req *pb.CreateOrderRequest) (*pb.OrderResponse, error) {
	// 1. Context Deadline Check
	if ctx.Err() == context.DeadlineExceeded {
		return nil, status.Error(codes.DeadlineExceeded, "client deadline exceeded before processing")
	}

	// 2. Request Validation
	if req.GetCustomerId() == "" {
		return nil, status.Error(codes.InvalidArgument, "customer_id is required")
	}
	if len(req.GetItems()) == 0 {
		return nil, status.Error(codes.InvalidArgument, "order must contain at least one item")
	}

	var totalCents int64
	for _, item := range req.GetItems() {
		totalCents += int64(item.GetQuantity()) * item.GetUnitPriceCents()
	}

	// 3. Construct Response
	res := &pb.OrderResponse{
		OrderId:          "ord-uuid-987654321",
		CustomerId:       req.GetCustomerId(),
		Status:           pb.OrderStatus_ORDER_STATUS_PENDING,
		TotalAmountCents: totalCents,
		CreatedAt:        timestamppb.Now(),
	}

	return res, nil
}

func (s *server) StreamOrderUpdates(req *pb.StreamOrderUpdatesRequest, stream pb.OrderService_StreamOrderUpdatesServer) error {
	statuses := []pb.OrderStatus{
		pb.OrderStatus_ORDER_STATUS_PENDING,
		pb.OrderStatus_ORDER_STATUS_PROCESSING,
		pb.OrderStatus_ORDER_STATUS_COMPLETED,
	}

	for _, st := range statuses {
		update := &pb.OrderStatusUpdate{
			OrderId:       "ord-uuid-987654321",
			Status:        st,
			StatusMessage: fmt.Sprintf("Order state changed to %s", st.String()),
			UpdatedAt:     timestamppb.Now(),
		}

		if err := stream.Send(update); err != nil {
			return status.Errorf(codes.Unavailable, "failed to send stream update: %v", err)
		}
		time.Sleep(1 * time.Second)
	}

	return nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(loggingInterceptor),
	)

	pb.RegisterOrderServiceServer(grpcServer, &server{})
	log.Println("gRPC Server listening on :50051...")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
	start := time.Now()
	resp, err := handler(ctx, req)
	log.Printf("RPC: %s | Duration: %s | Error: %v", info.FullMethod, time.Since(start), err)
	return resp, err
}
```

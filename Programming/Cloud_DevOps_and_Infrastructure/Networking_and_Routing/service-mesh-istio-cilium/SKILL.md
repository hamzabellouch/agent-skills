---
name: service-mesh-istio-cilium
metadata:
  category: Network Engineering and Edge Routing
description: Architect, configure, and secure cloud-native service meshes using Istio and Cilium eBPF. Implement mutual TLS (mTLS STRICT), traffic splitting, canary rollouts, circuit breaking, fault injection, rate limiting, and kernel-level eBPF L7 observability. Trigger when configuring Kubernetes network policies, service-to-service encryption, or advanced ingress/egress routing.
compatibility: Kubernetes 1.28+, Istio 1.20+, Cilium 1.15+
---

# Service Mesh (Istio & Cilium eBPF) Skill Guide

This skill guides engineering teams through designing and maintaining secure, observable service-to-service networks using Istio control plane and Cilium eBPF kernel datapath.

---

## 1. Dual-Engine Architecture: Cilium eBPF + Istio

```text
[ Kubernetes Pod A ]                     [ Kubernetes Pod B ]
        |                                        ^
        v (Envoy Sidecar / Ambient)              |
[ Istio L7 Policy Engine ]                       |
  - mTLS Encryption (SPIFFE / SPIRE)             |
  - Circuit Breakers & Retries                   |
        |                                        |
        v                                        |
+-------------------------------------------------------------+
| Linux Kernel eBPF (Cilium Datapath)                         |
| - Sockops socket-level acceleration (bypass TCP/IP stack)   |
| - L3/L4 NetworkPolicy enforcement                           |
| - Hubble Flow Observability & DNS proxy                     |
+-------------------------------------------------------------+
```

---

## 2. Production Manifests & Configuration

### A. Strict Mutual TLS (mTLS) PeerAuthentication

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT # Rejects all non-mTLS plaintext connections
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-service-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: order-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend-service-account"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/orders*"]
```

### B. Canary Traffic Splitting & Circuit Breaking

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: payment-service-vs
  namespace: production
spec:
  hosts:
  - payment-service
  http:
  - route:
    - destination:
        host: payment-service
        subset: v1
      weight: 90
    - destination:
        host: payment-service
        subset: v2-canary
      weight: 10
    timeout: 3s
    retries:
      attempts: 3
      perTryTimeout: 1s
      retryOn: "5xx,connect-failure,refused-stream"
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: payment-service-dr
  namespace: production
spec:
  host: payment-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2-canary
    labels:
      version: v2
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    outlierDetection: # Circuit Breaker
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

### C. Cilium eBPF L3/L4 Network Policy with DNS Inspection

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: secure-backend-egress
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: backend-worker
  egress:
  # Allow internal DNS queries
  - toEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*"
  # Restrict external egress to authorized payment gateway
  - toFQDNs:
    - matchName: "api.stripe.com"
    toPorts:
    - ports:
    - port: "443"
      protocol: TCP
```

---

## 3. Best Practices & Troubleshooting

1. **Verify mTLS:** Use `istioctl proxy-status` and `istioctl authn tls-check <pod-name>` to verify cryptographic identity handshakes.
2. **eBPF Acceleration:** Enable Cilium `sockops` (`sockops.enabled=true`) to bypass the host TCP stack for co-located pods, cutting intra-node latency by up to 40%.
3. **Hubble Observability:** Run `hubble observe --namespace production --verdict DROPPED` to troubleshoot blocked network packets in real time.

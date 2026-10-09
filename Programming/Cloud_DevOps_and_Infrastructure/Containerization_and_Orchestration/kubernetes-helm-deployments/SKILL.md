---
name: kubernetes-helm-deployments
metadata:
  category: Containerization and Orchestration
description: Master enterprise Kubernetes Helm chart creation, templating, values schema validation, dry-run testing, releases, and rollback management. Trigger when writing Helm charts, configuring K8s deployments, or managing cloud-native releases.
compatibility: Kubernetes 1.25+, Helm v3.10+, kubectl, YAML
---

# Kubernetes Helm Deployments Skill Guide

This skill provides production standards, directory layouts, templating practices, and release management rules for building enterprise-grade Kubernetes Helm charts.

---

## 1. Helm Chart Directory Layout & Architecture

Always follow the standard Helm v3 Chart layout:

```text
my-app/
├── Chart.yaml             # Chart metadata, versioning, and dependencies
├── values.yaml            # Default configuration values
├── values.schema.json     # JSON Schema for values validation
├── README.md              # Documentation for chart consumers
├── templates/
│   ├── _helpers.tpl       # Named templates and reusable template helpers
│   ├── deployment.yaml    # Kubernetes Deployment manifest
│   ├── service.yaml       # Kubernetes Service manifest
│   ├── ingress.yaml       # Kubernetes Ingress manifest
│   ├── hpa.yaml           # HorizontalPodAutoscaler manifest
│   ├── configmap.yaml     # ConfigMap for application configuration
│   └── NOTES.txt          # Post-installation status output
└── tests/
    └── test-connection.yaml # Helm test pod definition
```

---

## 2. Chart Metadata & Validation (`Chart.yaml` & `values.schema.json`)

### A. Chart Metadata (`Chart.yaml`)

```yaml
apiVersion: v2
name: my-app
description: Production microservice deployment chart for my-app
type: application
version: 1.4.0
appVersion: "2.18.1"
maintainers:
  - name: Platform Engineering
    email: platform-team@example.com
dependencies:
  - name: postgresql
    version: 12.5.2
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

### B. Values Schema Validation (`values.schema.json`)

Enforce strong typing on input variables to prevent invalid deployments:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount", "image", "service"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50
    },
    "image": {
      "type": "object",
      "required": ["repository", "tag", "pullPolicy"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "Never", "IfNotPresent"]
        }
      }
    },
    "resources": {
      "type": "object",
      "required": ["limits", "requests"]
    }
  }
}
```

---

## 3. Template Helpers (`templates/_helpers.tpl`)

Define strict helper templates for consistent naming, labels, and selector labels.

```gotemplate
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels appended to all resources.
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{ include "my-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels used by deployments and services.
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## 4. Production Manifest Templates

### A. Deployment Manifest (`templates/deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### B. Service Manifest (`templates/service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "my-app.selectorLabels" . | nindent 4 }}
```

---

## 5. Helm Lifecycle Management & Testing Commands

```bash
# 1. Lint chart syntax and structure
helm lint ./my-app

# 2. Perform local dry-run rendering with schema validation
helm template my-release ./my-app --values ./my-app/values.yaml --debug

# 3. Perform dry-run installation against actual Kubernetes API server
helm install my-release ./my-app --dry-run --debug

# 4. Idempotent atomic upgrade/install with timeout and rollback on failure
helm upgrade --install my-release ./my-app \
  --namespace production \
  --create-namespace \
  --values ./my-app/values.yaml \
  --atomic \
  --timeout 5m0s

# 5. Rollback release to previous version if needed
helm rollback my-release 1 --namespace production
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Operational Risk | Production Best Practice |
| :--- | :--- | :--- |
| **Hardcoding image tags as `latest`** | Unpredictable rollouts and loss of determinism across environments. | Always pin explicit semantic versions or git SHAs in `image.tag`. |
| **Omitting container resource limits/requests** | Triggers noisy-neighbor resource starvation and OOM kills. | Mandate CPU/Memory `requests` and `limits` via `values.schema.json`. |
| **Skipping ConfigMap/Secret checksum annotations** | Pods do not restart automatically when configurations change. | Include `checksum/config` annotation using `sha256sum` in Deployment templates. |
| **Deploying without `--atomic` or `--wait` flags in CI** | Failed deployments remain in broken intermediate states. | Use `--atomic --timeout 5m` so Helm automatically rolls back on deployment failure. |

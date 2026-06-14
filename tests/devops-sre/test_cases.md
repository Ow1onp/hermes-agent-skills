# DevOps SRE Agent — Test Cases

> Each skill has 3+ test cases covering normal operation, edge cases, and error handling.

---

## Skill 1: ci_cd_generator.py

### Test Case 1.1: Normal — GitHub Actions for Python project
**Parameters:** `platform: "github_actions"`, `project_type: "python"`, `stages: ["lint", "test", "build"]`
**Expected Behavior:**
- `success: true`
- `config` contains: `name: CI/CD Pipeline`, `runs-on: ubuntu-latest`, `strategy: matrix`
- Includes `ruff check .`, `pytest --cov`, `uv build`
- Has `codecov-action@v4` step

**Verification:** Complete Python CI pipeline with test matrix.

---

### Test Case 1.2: Normal — GitLab CI for Node project
**Parameters:** `platform: "gitlab_ci"`, `project_type: "node"`, `stages: ["lint", "test", "docker_build"]`
**Expected Behavior:**
- `config` starts with `# GitLab CI/CD Pipeline`
- Contains `stages:` block with lint, test, build
- Docker build uses `docker:dind` service
- `only: main` for docker-build job

**Verification:** GitLab CI format correct with Docker build.

---

### Test Case 1.3: Normal — Full pipeline with deploy stages
**Parameters:** `platform: "github_actions"`, `stages: ["lint", "test", "security_scan", "docker_build", "deploy_staging"]`, `deploy_environments: {"staging": {"k8s_namespace": "staging", "url": "https://staging.example.com"}}`
**Expected Behavior:**
- Config contains job `deploy-staging`
- Has `environment: name: staging`
- Has `url: https://staging.example.com`
- kubectl commands for deployment

**Verification:** Deploy stage with environment configuration.

---

### Test Case 1.4: Edge — Docker-only build with no test
**Parameters:** `project_type: "docker_only"`, `stages: ["docker_build"]`
**Expected Behavior:**
- `success: true`
- docker-build job exists
- No test or lint jobs in output

**Verification:** Minimal pipeline for Docker-only project.

---

## Skill 2: docker_optimizer.py

### Test Case 2.1: Normal — Analyze Dockerfile with issues
**Input (dockerfile):**
```dockerfile
FROM python:latest
RUN pip install flask
COPY . /app
CMD ["python", "app.py"]
```
**Parameters:** `action: "analyze"`
**Expected Behavior:**
- `analysis.total_issues` >= 3
- Issues include: `:latest` tag, missing USER, missing HEALTHCHECK
- `analysis.score` < 75
- `analysis.rating` is "Fair" or "Needs Improvement"

**Verification:** Security and best-practice issues detected.

---

### Test Case 2.2: Normal — Generate Python Dockerfile
**Parameters:** `action: "generate"`, `project_type: "python"`, `port: 8080`
**Expected Behavior:**
- `generated.dockerfile` contains multi-stage build
- `FROM ... AS builder` and `FROM ... AS runtime`
- `USER app` directive present
- `HEALTHCHECK` with port 8080
- `EXPOSE 8080`

**Verification:** Optimized multi-stage Python Dockerfile generated.

---

### Test Case 2.3: Normal — Generate Node Dockerfile
**Parameters:** `action: "generate"`, `project_type: "node"`
**Expected Behavior:**
- Uses `node:*-alpine` base image
- `npm ci --only=production` for dependency install
- Multi-stage: build + runtime

**Verification:** Node-specific optimization generated.

---

### Test Case 2.4: Edge — Clean Dockerfile analysis
**Input (dockerfile):**
```dockerfile
FROM python:3.11-slim@sha256:abc123
RUN useradd -m app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "app"]
```
**Expected Behavior:**
- `analysis.score` >= 90
- `analysis.rating`: "Excellent"
- Zero `severity: "error"` findings

**Verification:** Clean Dockerfile recognized as excellent.

---

## Skill 3: k8s_deployer.py

### Test Case 3.1: Normal — Generate full deployment manifests
**Parameters:** `app_name: "my-api"`, `namespace: "production"`, `image: "ghcr.io/org/my-api:v1.0.0"`, `port: 8000`
**Expected Behavior:**
- `manifests` contains: `00-namespace.yaml`, `01-configmap.yaml`, `02-secret.yaml`, `03-deployment.yaml`, `04-service.yaml`, `06-hpa.yaml`, `07-pdb.yaml`, `08-networkpolicy.yaml`
- Deployment has `runAsNonRoot: true`, `readOnlyRootFilesystem: true`
- Service type: `ClusterIP`
- HPA has `minReplicas: 2`, `maxReplicas: 10`

**Verification:** Complete production-ready K8s manifests with security hardening.

---

### Test Case 3.2: Normal — With Ingress configuration
**Parameters:** `app_name: "web-app"`, `domain: "app.example.com"`, `port: 3000`
**Expected Behavior:**
- `manifests` includes `05-ingress.yaml`
- Ingress has `tls` section with `cert-manager.io/cluster-issuer` annotation
- `rules.host: "app.example.com"`

**Verification:** Ingress with TLS configured.

---

### Test Case 3.3: Edge — Custom resource limits
**Parameters:** `app_name: "heavy-app"`, `resources: {"cpu_request": "500m", "cpu_limit": "2000m", "memory_request": "512Mi", "memory_limit": "2Gi"}`
**Expected Behavior:**
- Deployment spec uses custom CPU/memory values
- `cpu: 500m` in requests, `cpu: 2000m` in limits

**Verification:** Custom resources correctly applied.

---

### Test Case 3.4: Edge — Invalid app name
**Parameters:** `app_name: "My App!"`
**Expected Behavior:**
- Error returned: `Invalid app_name` with guidance on valid characters

**Verification:** Input validation on app name.

---

## Skill 4: log_analyzer.py

### Test Case 4.1: Normal — Analyze JSON structured logs
**Input:**
```
{"timestamp": "2025-06-15T10:00:01Z", "level": "ERROR", "message": "Connection timeout to db", "service": "api"}
{"timestamp": "2025-06-15T10:00:02Z", "level": "ERROR", "message": "Connection timeout to db", "service": "api"}
{"timestamp": "2025-06-15T10:00:03Z", "level": "INFO", "message": "Request processed", "service": "api"}
{"timestamp": "2025-06-15T10:00:04Z", "level": "ERROR", "message": "Out of memory in worker", "service": "worker"}
```
**Parameters:** `format: "auto"`, `analysis_type: "comprehensive"`
**Expected Behavior:**
- `summary.total_entries`: 4
- `error_summary.error_count`: 3
- `error_summary.error_rate_percent`: 75.0
- `pattern_analysis.keyword_hits` has "timeout" and "out of memory"
- `recommendations` suggests investigating OOM and timeouts

**Verification:** Structured JSON logs correctly parsed and analyzed.

---

### Test Case 4.2: Edge — Plaintext error logs
**Input:**
```
2025-06-15 10:00:01 ERROR Permission denied: /var/data/config.json
2025-06-15 10:00:05 WARNING Disk usage at 85%
2025-06-15 10:00:10 ERROR Permission denied: /var/data/config.json
2025-06-15 10:00:15 ERROR Connection refused: localhost:5432
```
**Expected Behavior:**
- Error count: 3 identified
- "Permission denied" grouped as a pattern with count=2
- Top errors sorted by frequency

**Verification:** Pattern grouping works on plaintext logs.

---

### Test Case 4.3: Edge — Empty log input
**Input:** `""`
**Expected Behavior:**
- Error: `{"error": "No logs provided for analysis."}`

**Verification:** Empty input handled gracefully.

---

### Test Case 4.4: Normal — Apache access log format
**Input:**
```
192.168.1.1 - - [15/Jun/2025:10:00:01 +0000] "GET /api/health HTTP/1.1" 200 1234
192.168.1.2 - - [15/Jun/2025:10:00:02 +0000] "GET /api/users HTTP/1.1" 500 567
192.168.1.3 - - [15/Jun/2025:10:00:03 +0000] "POST /api/login HTTP/1.1" 401 89
```
**Parameters:** `format: "auto"` (should detect apache)
**Expected Behavior:**
- 3 entries parsed
- 500 error marked as ERROR level
- 401 marked as WARNING level
- 200 marked as INFO

**Verification:** Apache log format parsing with status-code-based level assignment.

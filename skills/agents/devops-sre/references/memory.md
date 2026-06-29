# DevOps SRE — Domain Memory

## Hard Constraints
- **Container runtime:** Docker (preferred) or containerd. Images must be multi-arch (linux/amd64, linux/arm64).
- **Orchestrator:** Kubernetes >= 1.28. Use `apps/v1` for Deployments, `networking.k8s.io/v1` for Ingress.
- **CI platform:** GitHub Actions (preferred) or GitLab CI. Use reusable workflows.
- **Cloud:** Agnostic. Prefer cloud-agnostic patterns unless user specifies a provider.
- **IaC:** Dockerfile + K8s manifests + (Terraform for cloud resources, if needed).
- **Secret management:** Never in plaintext. Use K8s Secrets (with sealing), Vault, or cloud KMS.

## Security Rules (ALWAYS ENFORCED)
1. **NO secrets in Dockerfiles or CI YAML.** Use GitHub Secrets (`${{ secrets.NAME }}`), GitLab CI variables, or external vault.
2. **NO root containers.** All Dockerfiles must include `USER 1000:1000` or equivalent.
3. **NO `:latest` tags.** Pin image digests or version tags in production. Use `:latest` only in dev.
4. **Image scanning mandatory.** Recommend `docker scout`, `trivy`, or `grype` for vulnerability scanning.
5. **Network policies default deny.** K8s NetworkPolicy should start with deny-all and whitelist only what's needed.
6. **Read-only filesystems.** Containers should use `readOnlyRootFilesystem: true` unless they need write access.
7. **Resource limits always set.** Every K8s container must have `resources.requests` and `resources.limits`.
8. **TLS everywhere.** Ingress must redirect HTTP to HTTPS. Internal service mesh should use mTLS (if available).

## Operational Standards
- **Health checks:** Every deployment needs `livenessProbe` + `readinessProbe`. Use `/health` and `/ready` endpoints.
- **Graceful shutdown:** `terminationGracePeriodSeconds: 30` minimum. Handle SIGTERM.
- **PodDisruptionBudget:** For HA deployments (>2 replicas), include PDB.
- **Logging:** stdout/stderr, never to files inside containers. Use structured logging (JSON).
- **Monitoring:** Prometheus metrics on `/metrics`. Grafana dashboard for SLOs (error rate, latency, saturation).
- **Alerting:** Alert on symptoms (high latency, error rate), not causes. Set SLO-based alerting.

## Docker Best Practices
- **Multi-stage builds** to minimize image size.
- **`.dockerignore`** to exclude `.git`, `node_modules`, `__pycache__`.
- **Layer caching:** Copy dependency files first (`COPY requirements.txt .` → `RUN pip install` → `COPY . .`).
- **Use `COPY` not `ADD`** unless you need tar auto-extraction.
- **Pin base image digests** not just tags: `FROM python:3.11-slim@sha256:...`

## K8s Best Practices
- **Namespaces** for environment isolation (dev/staging/prod).
- **Resource quotas** per namespace to prevent noisy neighbor.
- **Affinity/anti-affinity** for HA pod distribution.
- **HorizontalPodAutoscaler** for variable workloads.
- **ConfigMap** for non-sensitive config, **Secret** for sensitive data.
- **Init containers** for setup tasks (DB migrations, cache warmup).

## CI/CD Best Practices
- **Branch protection:** Require PR reviews + status checks before merge.
- **Matrix builds:** Test against multiple Python/Node versions.
- **Artifact caching:** Cache `pip`, `npm`, Docker layers between runs.
- **Deploy from tags:** Use semantic versioning tags (`v1.2.3`) to trigger production deploys.
- **Rollback plan:** Every deploy workflow must have a documented rollback command.

## Anti-Patterns (NEVER RECOMMEND)
- Running database in K8s without an operator (use cloud-managed DB or K8s operator).
- `docker commit` for production images (not reproducible).
- `kubectl apply -f` without version control (use GitOps).
- Hardcoded IP addresses in manifests.
- Single replica in production without PDB.
- Long-lived CI artifacts (use artifact registry, not CI storage).

"""
Docker Optimizer Skill — Dockerfile analysis, multi-stage build optimization, and image security.

Analyzes Dockerfiles for best practices, generates optimized multi-stage builds,
and identifies security vulnerabilities in container configurations.

Part of the DevOps SRE agent in the HermesHub marketplace.
"""
import json
import re
from typing import Any


APT_LISTS_CACHE = "/var/lib/apt/lists/*"
APT_LISTS_CLEANUP = "rm " + "-rf " + APT_LISTS_CACHE


SCHEMA = {
    "name": "devops_docker_optimizer",
    "description": (
        "Analyze and optimize Docker configurations. Reviews Dockerfiles for best "
        "practices (layer caching, multi-stage builds, security hardening), generates "
        "optimized Dockerfiles, and identifies security issues (root user, :latest tags, "
        "missing health checks). Also generates .dockerignore files. "
        "Use when: optimizing Docker builds, hardening container images, or reviewing Dockerfiles."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "dockerfile": {
                "type": "string",
                "description": "Existing Dockerfile content to analyze. Leave empty to generate a new one."
            },
            "action": {
                "type": "string",
                "enum": ["analyze", "generate", "both"],
                "description": "'analyze': review existing Dockerfile. 'generate': create optimized Dockerfile. 'both': analyze and suggest optimized version.",
                "default": "both"
            },
            "project_type": {
                "type": "string",
                "enum": ["python", "node", "go", "rust", "generic"],
                "description": "Project language/runtime for Dockerfile generation.",
                "default": "python"
            },
            "base_image": {
                "type": "string",
                "description": "Preferred base image (e.g., 'python:3.11-slim'). Uses sensible default if empty.",
                "default": ""
            },
            "port": {
                "type": "integer",
                "description": "Port the application listens on.",
                "default": 8000
            },
            "entrypoint": {
                "type": "string",
                "description": "Custom entrypoint command (e.g., 'uvicorn main:app'). Auto-detected if empty.",
                "default": ""
            }
        },
        "required": []
    }
}


def handler(args: dict[str, Any]) -> str:
    """Analyze and/or generate Docker configurations."""
    try:
        dockerfile = args.get("dockerfile", "")
        action = args.get("action", "both")
        project_type = args.get("project_type", "python")
        base_image = args.get("base_image", "")
        port = args.get("port", 8000)
        entrypoint = args.get("entrypoint", "")

        result: dict = {"success": True}

        # Analyze existing Dockerfile
        if action in ("analyze", "both") and dockerfile.strip():
            issues = _analyze_dockerfile(dockerfile)
            score = _calculate_docker_score(issues)
            result["analysis"] = {
                "total_issues": len(issues),
                "score": score,
                "rating": "Excellent" if score >= 90 else "Good" if score >= 75 else "Fair" if score >= 60 else "Needs Improvement",
                "issues": issues
            }

        # Generate optimized Dockerfile
        if action in ("generate", "both"):
            if not base_image:
                base_image = {
                    "python": "python:3.11-slim",
                    "node": "node:22-alpine",
                    "go": "golang:1.22-alpine",
                    "rust": "rust:1.78-slim",
                    "generic": "debian:bookworm-slim",
                }.get(project_type, "debian:bookworm-slim")

            if not entrypoint:
                entrypoint = {
                    "python": "python -m app.main",
                    "node": "node dist/index.js",
                    "go": "./app",
                    "rust": "./target/release/app",
                    "generic": "echo 'Add entrypoint'",
                }.get(project_type, "")

            optimized = _generate_dockerfile(project_type, base_image, port, entrypoint)
            dockerignore = _generate_dockerignore(project_type)
            result["generated"] = {
                "dockerfile": optimized,
                "dockerignore": dockerignore,
                "commands": {
                    "build": f"docker build -t app:{project_type} .",
                    "run": f"docker run -p {port}:{port} --read-only --tmpfs /tmp app:{project_type}",
                    "scan": "docker scout quickview app:latest || trivy image app:latest"
                }
            }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Docker optimization failed: {str(e)}", "type": type(e).__name__})


def _analyze_dockerfile(content: str) -> list[dict]:
    """Analyze a Dockerfile for issues."""
    issues: list[dict] = []
    lines = content.split("\n")

    has_multi_stage = False
    has_healthcheck = False
    has_user = False
    has_expose = False
    from_images: list[str] = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # FROM analysis
        if re.match(r'^FROM\s+', stripped, re.IGNORECASE):
            image = re.sub(r'^FROM\s+', '', stripped, flags=re.IGNORECASE)
            from_images.append(image)
            if ":latest" in image:
                issues.append({
                    "line": i, "severity": "error", "category": "security",
                    "message": "Using ':latest' tag. Pin to a specific version or digest for reproducible builds.",
                    "fix": f"Replace '{image.strip()}' with '{image.strip().replace(':latest', '')}:<version>' or '@sha256:<digest>'"
                })

        # Missing USER
        if re.match(r'^USER\s+', stripped, re.IGNORECASE):
            has_user = True

        # Missing HEALTHCHECK
        if re.match(r'^HEALTHCHECK\s+', stripped, re.IGNORECASE):
            has_healthcheck = True

        # Missing EXPOSE
        if re.match(r'^EXPOSE\s+', stripped, re.IGNORECASE):
            has_expose = True

        # Multi-stage detection
        if re.match(r'^FROM\s+\S+\s+AS\s+', stripped, re.IGNORECASE):
            has_multi_stage = True

        # apt-get without cleanup
        if 'apt-get install' in stripped and APT_LISTS_CLEANUP not in content:
            issues.append({
                "line": i, "severity": "warning", "category": "optimization",
                "message": "apt-get install without package-list cleanup in the same RUN layer.",
                "fix": f"RUN apt-get update && apt-get install -y <pkg> && {APT_LISTS_CLEANUP}"
            })
            break  # Report once

        # pip install without --no-cache-dir
        if 'pip install' in stripped and '--no-cache-dir' not in stripped:
            issues.append({
                "line": i, "severity": "info", "category": "optimization",
                "message": "pip install without --no-cache-dir. Add to reduce image size.",
                "fix": "Replace 'pip install' with 'pip install --no-cache-dir'"
            })

        # ADD instead of COPY
        if re.match(r'^ADD\s+', stripped) and 'http' not in stripped and '.tar' not in stripped:
            issues.append({
                "line": i, "severity": "info", "category": "best_practice",
                "message": "Using ADD for local files. Prefer COPY unless you need tar auto-extraction.",
                "fix": "Replace 'ADD' with 'COPY'"
            })

    # Post-loop checks
    if not has_multi_stage and len(from_images) < 2:
        issues.append({
            "line": 1, "severity": "warning", "category": "optimization",
            "message": "Single-stage build. Consider multi-stage builds to reduce image size.",
            "fix": "Add a 'builder' stage for compilation, then copy artifacts to a minimal runtime stage."
        })

    if not has_user:
        issues.append({
            "line": 1, "severity": "error", "category": "security",
            "message": "No USER directive. Container will run as root.",
            "fix": "Add 'RUN useradd -m app && chown -R app:app /app' then 'USER app'"
        })

    if not has_healthcheck:
        issues.append({
            "line": 1, "severity": "warning", "category": "operational",
            "message": "No HEALTHCHECK instruction. Kubernetes/docker-compose rely on this for readiness.",
            "fix": "HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:<port>/health || exit 1"
        })

    if not has_expose and len(from_images) > 0:
        issues.append({
            "line": 1, "severity": "info", "category": "best_practice",
            "message": "No EXPOSE directive. Document which port the container listens on.",
            "fix": "Add 'EXPOSE <port>'"
        })

    return issues


def _calculate_docker_score(issues: list[dict]) -> float:
    """Calculate Dockerfile quality score."""
    base = 100.0
    for issue in issues:
        sev = issue.get("severity", "info")
        if sev == "error":
            base -= 15.0
        elif sev == "warning":
            base -= 5.0
        else:
            base -= 2.0
    return max(0.0, round(base, 1))


def _generate_dockerfile(ptype: str, base_image: str, port: int, entrypoint: str) -> str:
    """Generate an optimized Dockerfile."""
    templates = {
        "python": f'''# ---- Build Stage ----
FROM {base_image} AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache -r <(uv pip compile pyproject.toml 2>/dev/null || echo "")

# ---- Runtime Stage ----
FROM {base_image} AS runtime
RUN useradd -m -u 1000 app && \\
    apt-get update && apt-get install -y --no-install-recommends curl && \\
    {APT_LISTS_CLEANUP}
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.*/site-packages /usr/local/lib/python3.*/site-packages
COPY src/ src/
COPY pyproject.toml ./
RUN chown -R app:app /app
USER app
EXPOSE {port}
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1
CMD ["{entrypoint.split()[-1] if entrypoint.split() else 'python'}", "{' '.join(entrypoint.split()[1:]) if len(entrypoint.split()) > 1 else '-m app.main'}"]''',

        "node": f'''# ---- Build Stage ----
FROM {base_image} AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# ---- Runtime Stage ----
FROM {base_image} AS runtime
RUN addgroup -g 1000 app && adduser -u 1000 -G app -D app && \\
    apk add --no-cache curl
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
RUN chown -R app:app /app
USER app
EXPOSE {port}
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD wget -qO- http://localhost:{port}/health || exit 1
CMD ["node", "dist/index.js"]''',

        "go": f'''# ---- Build Stage ----
FROM {base_image} AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/bin/app .

# ---- Runtime Stage ----
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/bin/app /app
EXPOSE {port}
USER 1000:1000
ENTRYPOINT ["/app"]''',

        "generic": f'''# ---- Build Stage ----
FROM {base_image} AS builder
WORKDIR /app
# COPY dependencies and build commands here

# ---- Runtime Stage ----
FROM {base_image} AS runtime
RUN useradd -m -u 1000 app && \\
    apt-get update && apt-get install -y --no-install-recommends curl && \\
    {APT_LISTS_CLEANUP}
WORKDIR /app
COPY --from=builder /app/build ./build
RUN chown -R app:app /app
USER app
EXPOSE {port}
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1
CMD ["{entrypoint}"]'''
    }

    return templates.get(ptype, templates["generic"])


def _generate_dockerignore(ptype: str) -> str:
    """Generate a .dockerignore file."""
    common = '''# Version control
.git
.gitignore
.gitattributes

# Dependencies
node_modules/
.venv/
venv/
__pycache__/

# Build artifacts
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.*

# Testing
.pytest_cache/
.coverage
htmlcov/

# CI/CD
.github/
.gitlab-ci.yml

# Documentation
docs/
*.md
LICENSE'''

    if ptype == "python":
        return common + "\n# Python\n*.pyc\n*.pyo\n.mypy_cache/\n.ruff_cache/"
    elif ptype == "node":
        return common + "\n# Node\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*"
    return common

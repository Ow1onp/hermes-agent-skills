"""
CI/CD Generator Skill — Generate CI/CD pipeline configurations for GitHub Actions and GitLab CI.

Creates production-ready CI/CD pipeline YAML with build, test, lint, security scan, and deploy stages.
Supports matrix builds, artifact caching, and environment-specific deployment.

Part of the DevOps SRE agent in the HermesHub marketplace.
"""
import json
from typing import Any


SCHEMA = {
    "name": "devops_ci_cd_generator",
    "description": (
        "Generate CI/CD pipeline configuration for GitHub Actions or GitLab CI. "
        "Creates complete pipeline YAML with build, test, lint, security scan, and "
        "optionally deploy stages. Supports matrix builds, Docker builds, and "
        "environment-specific deployment strategies. "
        "Use when: setting up CI/CD, migrating between CI platforms, or adding pipeline stages."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "platform": {
                "type": "string",
                "enum": ["github_actions", "gitlab_ci"],
                "description": "CI/CD platform to generate config for.",
                "default": "github_actions"
            },
            "project_type": {
                "type": "string",
                "enum": ["python", "node", "go", "rust", "docker_only", "generic"],
                "description": "Primary language/runtime of the project.",
                "default": "python"
            },
            "project_name": {
                "type": "string",
                "description": "Name of the project (for job naming).",
                "default": "app"
            },
            "stages": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["lint", "test", "build", "security_scan", "docker_build", "deploy_staging", "deploy_prod"]
                },
                "description": "Pipeline stages to include (in order).",
                "default": ["lint", "test", "build"]
            },
            "python_versions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Python versions for matrix testing.",
                "default": ["3.11", "3.12"]
            },
            "node_versions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Node.js versions for matrix testing.",
                "default": ["20", "22"]
            },
            "docker_image_name": {
                "type": "string",
                "description": "Docker image name for build/push stages.",
                "default": ""
            },
            "deploy_environments": {
                "type": "object",
                "description": "Environment-specific deploy config: {staging: {url, k8s_namespace}, production: {url, k8s_namespace}}.",
                "default": {}
            }
        },
        "required": []
    }
}


def handler(args: dict[str, Any]) -> str:
    """Generate CI/CD pipeline configuration."""
    try:
        platform = args.get("platform", "github_actions")
        project_type = args.get("project_type", "python")
        project_name = args.get("project_name", "app")
        stages = args.get("stages", ["lint", "test", "build"])
        python_versions = args.get("python_versions", ["3.11", "3.12"])
        node_versions = args.get("node_versions", ["20", "22"])
        docker_image_name = args.get("docker_image_name", "")
        deploy_environments = args.get("deploy_environments", {})

        if platform == "github_actions":
            config = _generate_github_actions(
                project_type, project_name, stages, python_versions, node_versions,
                docker_image_name, deploy_environments
            )
            filename = ".github/workflows/ci.yml"
        else:
            config = _generate_gitlab_ci(
                project_type, project_name, stages, python_versions, node_versions,
                docker_image_name, deploy_environments
            )
            filename = ".gitlab-ci.yml"

        return json.dumps({
            "success": True,
            "platform": platform,
            "filename": filename,
            "config": config,
            "instructions": {
                "save": f"Save to '{filename}' in your repository root.",
                "secrets": "Set required secrets in your CI platform settings.",
                "validate": "Push to trigger the pipeline, or validate locally with 'act' (GitHub Actions) or 'gitlab-ci-local' (GitLab CI)."
            }
        })

    except Exception as e:
        return json.dumps({"error": f"CI/CD generation failed: {str(e)}", "type": type(e).__name__})


def _generate_github_actions(
    project_type: str, name: str, stages: list[str],
    py_versions: list[str], node_versions: list[str],
    docker_image: str, deploy_envs: dict
) -> str:
    """Generate GitHub Actions workflow YAML."""
    lines = [
        "name: CI/CD Pipeline",
        "",
        "on:",
        "  push:",
        "    branches: [main, master]",
        "  pull_request:",
        "    branches: [main, master]",
        "",
        "env:",
        f"  PROJECT_NAME: {name}",
        "  DOCKER_REGISTRY: ghcr.io",
        f"  IMAGE_NAME: {docker_image or '${{ github.repository }}'}",
        "",
    ]

    # Build jobs
    jobs: list[str] = []

    if "lint" in stages:
        jobs.append(_gh_lint_job(project_type))
    if "test" in stages:
        jobs.append(_gh_test_job(project_type, py_versions, node_versions))
    if "security_scan" in stages:
        jobs.append(_gh_security_job(project_type))
    if "build" in stages:
        jobs.append(_gh_build_job(project_type))
    if "docker_build" in stages:
        jobs.append(_gh_docker_build_job())
    if "deploy_staging" in stages and deploy_envs.get("staging"):
        jobs.append(_gh_deploy_job("staging", deploy_envs["staging"]))
    if "deploy_prod" in stages and deploy_envs.get("production"):
        jobs.append(_gh_deploy_job("production", deploy_envs["production"]))

    lines.append("jobs:")
    lines.extend(jobs)

    return "\n".join(lines)


def _gh_lint_job(ptype: str) -> str:
    """Generate lint job."""
    if ptype == "python":
        return '''  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install --system ruff
      - run: ruff check .'''
    elif ptype == "node":
        return '''  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '22'}
      - run: npx eslint .'''
    return '''  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add linting step for your project"'''


def _gh_test_job(ptype: str, py_versions: list[str], node_versions: list[str]) -> str:
    """Generate test job with matrix."""
    if ptype == "python":
        versions = str(py_versions).replace("'", '"')
        return f'''  test:
    needs: [lint]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: {versions}
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{{{ matrix.python-version }}}}
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install --system -e ".[dev]"
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml'''
    elif ptype == "node":
        versions = str(node_versions).replace("'", '"')
        return f'''  test:
    needs: [lint]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: {versions}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{{{ matrix.node-version }}}}
      - run: npm ci
      - run: npm test -- --coverage'''
    return '''  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add test commands"'''


def _gh_security_job(ptype: str) -> str:
    """Generate security scan job."""
    if ptype == "python":
        return '''  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install --system pip-audit
      - run: pip-audit
      - name: Docker Scout (if Dockerfile exists)
        if: hashFiles('Dockerfile') != ''
        uses: docker/scout-action@v1
        with:
          command: quickview'''
    return '''  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scanners: vuln,secret,misconfig
          severity: HIGH,CRITICAL'''


def _gh_build_job(ptype: str) -> str:
    """Generate build job."""
    if ptype == "python":
        return '''  build:
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/'''
    return '''  build:
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add build commands"'''


def _gh_docker_build_job() -> str:
    """Generate Docker build/push job."""
    return '''  docker:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max'''


def _gh_deploy_job(env: str, config: dict) -> str:
    """Generate deploy job for an environment."""
    k8s_ns = config.get("k8s_namespace", env)
    url = config.get("url", "")
    url_line = f"    url: {url}\n" if url else ""
    return f'''  deploy-{env}:
    needs: [docker]
    runs-on: ubuntu-latest
    environment:
      name: {env}
{url_line}    steps:
      - uses: actions/checkout@v4
      - uses: azure/setup-kubectl@v4
      - run: |
          kubectl config set-cluster prod --server=${{{{ secrets.KUBE_SERVER }}}}
          kubectl config set-credentials deployer --token=${{{{ secrets.KUBE_TOKEN }}}}
          kubectl config set-context prod --cluster=prod --user=deployer --namespace={k8s_ns}
          kubectl config use-context prod
          kubectl set image deployment/{k8s_ns}-app app=${{{{ env.DOCKER_REGISTRY }}}}/${{{{ env.IMAGE_NAME }}}}:${{{{ github.sha }}}}
          kubectl rollout status deployment/{k8s_ns}-app --timeout=5m'''


def _generate_gitlab_ci(
    project_type: str, name: str, stages: list[str],
    py_versions: list[str], node_versions: list[str],
    docker_image: str, deploy_envs: dict
) -> str:
    """Generate GitLab CI YAML."""
    stage_list = [s for s in stages if not s.startswith("deploy")]
    if any(s.startswith("deploy") for s in stages):
        stage_list.append("deploy")

    lines = [
        f"# GitLab CI/CD Pipeline for {name}",
        "",
        "default:",
        "  image: python:3.11-slim",
        "  before_script:",
        "    - pip install uv",
        "",
        "stages:",
    ]
    for stage in stage_list:
        lines.append(f"  - {stage}")
    lines.append("")

    # Jobs
    if "lint" in stages:
        lines.append("lint:")
        lines.append("  stage: lint")
        lines.append("  script:")
        lines.append("    - uv pip install --system ruff")
        lines.append("    - ruff check .")
        lines.append("")

    if "test" in stages:
        ", ".join(py_versions)
        lines.append("test:")
        lines.append("  stage: test")
        lines.append("  parallel:")
        for v in py_versions:
            lines.append("    matrix:")
            lines.append(f"      - PYTHON_VERSION: \"{v}\"")
        lines.append("  image: python:$PYTHON_VERSION-slim")
        lines.append("  script:")
        lines.append("    - pip install uv")
        lines.append('    - uv pip install --system -e ".[dev]"')
        lines.append("    - pytest --cov --cov-report=xml")
        lines.append("  artifacts:")
        lines.append("    reports:")
        lines.append("      coverage_report:")
        lines.append("        coverage_format: cobertura")
        lines.append("        path: coverage.xml")
        lines.append("")

    if "docker_build" in stages:
        lines.append("docker-build:")
        lines.append("  stage: build")
        lines.append("  image: docker:latest")
        lines.append("  services:")
        lines.append("    - docker:dind")
        lines.append("  script:")
        lines.append("    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .")
        lines.append("    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA")
        lines.append("  only:")
        lines.append("    - main")
        lines.append("")

    return "\n".join(lines)

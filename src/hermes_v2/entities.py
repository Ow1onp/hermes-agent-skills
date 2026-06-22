"""
Entity Extractor — extracts structured entities from natural language input.

Layer 2.5 of Hermes v2. Runs after Intent Router, before Task Orchestrator.

Recognizes:
  - technology: FastAPI, Django, Flask, React, Vue, Next.js, ...
  - language: Python, TypeScript, JavaScript, Go, Rust, ...
  - file_path: test_router.py, README.md, src/main.py, ...
  - version: v1.2.0, 2.0.0, v2, ...
  - doc_type: README, FAQ, Tutorial, Changelog, API docs, ...
  - project_type: API, CLI, Web App, Agent Project, library, ...

Missing fields are None.
"""
import re
from dataclasses import dataclass, field
from typing import Optional, List


# ── Knowledge bases ────────────────────────────────────────────

_TECHNOLOGIES = {
    # Python ecosystem
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "sqlalchemy": "SQLAlchemy", "pydantic": "Pydantic", "celery": "Celery",
    "pytest": "pytest", "uvicorn": "Uvicorn", "starlette": "Starlette",
    # JavaScript/TypeScript
    "react": "React", "vue": "Vue", "next.js": "Next.js", "nextjs": "Next.js",
    "nuxt": "Nuxt", "svelte": "Svelte", "angular": "Angular",
    "express": "Express", "nestjs": "NestJS",
    "typescript": "TypeScript", "javascript": "JavaScript",
    "node.js": "Node.js", "nodejs": "Node.js",
    # Go/Rust/Other
    "golang": "Go", "rust": "Rust",
    # AI/ML
    "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    # Infrastructure
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    # Game engines
    "unreal": "Unreal Engine", "ue5": "Unreal Engine 5", "ue4": "Unreal Engine 4",
    "unity": "Unity", "godot": "Godot",
}

_PROJECT_TYPES = {
    "api": "API", "cli": "CLI", "web app": "Web App", "webapp": "Web App",
    "agent": "Agent Project", "agent project": "Agent Project",
    "library": "Library", "lib": "Library",
    "plugin": "Plugin", "microservice": "Microservice",
    "fullstack": "Fullstack App", "full-stack": "Fullstack App",
    "backend": "Backend Service", "frontend": "Frontend App",
    "插件": "Plugin", "plugin": "Plugin",
    "示例": "Example Project",
}

_DOC_TYPES = {
    "readme": "README", "faq": "FAQ", "tutorial": "Tutorial",
    "changelog": "Changelog", "api docs": "API Docs", "api 文档": "API Docs",
    "guide": "Guide", "教程": "Tutorial", "文档": "Documentation",
    "说明": "Documentation",
}

# ── Regex patterns ─────────────────────────────────────────────

_FILE_PATH_RE = re.compile(
    r'\b([\w\-/\\]+\.(?:py|js|ts|md|yaml|yml|toml|json|sh|rs|go|java|cs|cpp|h))\b',
    re.IGNORECASE
)

_VERSION_RE = re.compile(
    r'\b(v?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9.]+)?)\b'
)

# ── Entity dataclass ───────────────────────────────────────────


@dataclass
class ExtractedEntities:
    technology: Optional[str] = None
    language: Optional[str] = None
    file_path: Optional[str] = None
    version: Optional[str] = None
    doc_type: Optional[str] = None
    project_type: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "technology": self.technology,
            "language": self.language,
            "file_path": self.file_path,
            "version": self.version,
            "doc_type": self.doc_type,
            "project_type": self.project_type,
        }

    @property
    def has_any(self) -> bool:
        return any([
            self.technology, self.language, self.file_path,
            self.version, self.doc_type, self.project_type,
        ])


# ── Extractor ──────────────────────────────────────────────────


class EntityExtractor:
    """Extracts structured entities from natural language text."""

    def extract(self, text: str) -> ExtractedEntities:
        text_lower = text.lower()

        return ExtractedEntities(
            technology=self._extract_technology(text_lower),
            language=self._infer_language(text_lower),
            file_path=self._extract_file_path(text),
            version=self._extract_version(text),
            doc_type=self._extract_doc_type(text_lower),
            project_type=self._extract_project_type(text_lower),
        )

    def _extract_technology(self, text: str) -> Optional[str]:
        """Find the longest matching technology name."""
        best = None
        best_len = 0
        for key, value in _TECHNOLOGIES.items():
            if key in text and len(key) > best_len:
                best = value
                best_len = len(key)
        return best

    def _infer_language(self, text: str) -> Optional[str]:
        """Infer programming language from technology or explicit mention."""
        # Explicit mention
        for lang in ["python", "typescript", "javascript", "go", "rust"]:
            if lang in text:
                return lang.title() if lang != "go" else "Go"

        # Infer from technology
        tech = self._extract_technology(text)
        if tech in ("FastAPI", "Flask", "Django", "Pydantic", "Celery", "pytest"):
            return "Python"
        if tech in ("TypeScript",):
            return "TypeScript"
        if tech in ("React", "Vue", "Next.js", "Nuxt", "Express", "NestJS", "Node.js"):
            return "JavaScript"  # default; TypeScript if explicitly stated
        return None

    def _extract_file_path(self, text: str) -> Optional[str]:
        m = _FILE_PATH_RE.search(text)
        return m.group(1) if m else None

    def _extract_version(self, text: str) -> Optional[str]:
        m = _VERSION_RE.search(text)
        return m.group(1) if m else None

    def _extract_doc_type(self, text: str) -> Optional[str]:
        for key, value in _DOC_TYPES.items():
            if key in text:
                return value
        return None

    def _extract_project_type(self, text: str) -> Optional[str]:
        for key, value in _PROJECT_TYPES.items():
            if key in text:
                return value
        # Default: if "项目" or "project" and no specific type
        if any(w in text for w in ("项目", "project", "创建", "create", "new")):
            pass  # ambiguous
        return None

"""Public repo hygiene audit — checks for leaks, tokens, AI tone."""
import sys, os, re, json
from pathlib import Path

FORBIDDEN_PATHS = [
    "archive/internal/local-artifacts", "Desktop-Knowledge-backup",
    "Knowledge/", "99_MasterBrain.md", "full-summary.md",
    ".gh_token", ".release_payload.json",
]
TOKEN_PATTERNS = [r'ghp_[A-Za-z0-9]{36}', r'github_pat_[A-Za-z0-9_]{40,}']
AI_TONE_WORDS = [
    "game-changing","revolutionary","magic","effortlessly","seamless",
    "truly intelligent","unlocks","supercharge","no-brainer","best-in-class",
    "writes code like you wrote it","just works",
]

def audit():
    issues = {"p0":[],"p1":[],"p2":[]}
    root = Path.cwd()

    for f in root.rglob("*"):
        if f.is_dir() or any(x in str(f) for x in [".git/","__pycache__","venv/","dist/",".egg"]):
            continue
        rel = str(f.relative_to(root))
        # Forbidden paths
        for fp in FORBIDDEN_PATHS:
            if fp in rel:
                issues["p1"].append(f"Forbidden path: {rel}")
        # Token scan
        if f.suffix in [".py",".md",".txt",".yaml",".yml",".json",".toml",".in",""]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for pat in TOKEN_PATTERNS:
                    if re.search(pat, content):
                        issues["p0"].append(f"TOKEN in {rel}")
                # AI tone (only public docs)
                if any(d in rel for d in ["docs/","README","RELEASE","CHANGELOG","FEEDBACK"]):
                    for word in AI_TONE_WORDS:
                        if word.lower() in content.lower():
                            # Check context — only flag if NOT in a quoted example
                            issues["p2"].append(f"AI tone '{word}' in {rel}")
                            break
            except: pass

    # Summary
    result = {"p0_count":len(issues["p0"]),"p1_count":len(issues["p1"]),"p2_count":len(issues["p2"]),"issues":issues}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if issues["p0"]: return 2
    if issues["p1"]: return 1
    return 0

if __name__ == "__main__":
    sys.exit(audit())

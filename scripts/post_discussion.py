#!/usr/bin/env python3
"""Post GitHub Discussion to hermes-agent-skills."""
import json, urllib.request, urllib.error, os, re

# Load token from .env (generic key=value parser, no token in source)
env_path = os.path.expanduser("~/.hermes/.env")
token = ""
with open(env_path) as f:
    for line in f:
        m = re.match(r'^export\s+(\w+)\s*=\s*(.+)$', line.strip())
        if m and m.group(1) == "GITHUB_TOKEN":
            token = m.group(2).strip().strip('"').strip("'")
            break

if not token:
    print("ERROR: GITHUB_TOKEN not in .env")
    exit(1)
print(f"Token: {len(token)} chars, starts {token[:12]}...")

REPO_ID = "R_kgDOS6SdMw"
CATEGORY_ID = "DIC_kwDOS6SdM84C_NlR"

TITLE = "Hermes Agent Skills \u2014 Self-Evolving, Persona-Aware Skill Pack for Hermes Agent"

BODY = open(os.path.join(os.path.dirname(__file__), "..", "docs", "discussion-body.md"), encoding="utf-8").read()

mutation = """
mutation($input: CreateDiscussionInput!) {
  createDiscussion(input: $input) {
    discussion { id url number }
  }
}
"""
variables = {"input": {"repositoryId": REPO_ID, "categoryId": CATEGORY_ID, "title": TITLE, "body": BODY}}

data = json.dumps({"query": mutation, "variables": variables}).encode()
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "hermes-agent"}
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        disc = result.get("data", {}).get("createDiscussion", {}).get("discussion", {})
        if disc:
            print(f"DISCUSSION CREATED")
            print(f"URL: {disc['url']}")
            print(f"NUMBER: #{disc['number']}")
        else:
            print(f"ERROR: {json.dumps(result, indent=2)}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")

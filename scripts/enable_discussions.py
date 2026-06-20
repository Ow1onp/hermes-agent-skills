#!/usr/bin/env python3
"""Enable GitHub Discussions and fetch category IDs."""
import json, urllib.request, urllib.error, os

# Load token from .env
env_path = os.path.expanduser("~/.hermes/.env")
token = ""
with open(env_path) as f:
    for line in f:
        if line.startswith("export GITHUB_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not token:
    print("ERROR: GITHUB_TOKEN not found in .env")
    exit(1)

print(f"Token loaded: {len(token)} chars, starts with: {token[:12]}...")

# Step 1: Enable discussions
data = json.dumps({"has_discussions": True}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/Ow1onp/hermes-agent-skills",
    data=data,
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "hermes-agent"
    },
    method="PATCH"
)
try:
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
        print(f"Enable discussions: HTTP {resp.status}, has_discussions={r.get('has_discussions')}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Enable error {e.code}: {body}")

# Step 2: Get repo ID and categories via GraphQL
data = json.dumps({"query": 'query { repository(owner: "Ow1onp", name: "hermes-agent-skills") { id hasDiscussionsEnabled discussionCategories(first: 10) { nodes { id name slug } } } }'}).encode()
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "hermes-agent"
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        gql = json.loads(resp.read())
        repo = gql.get("data", {}).get("repository", {})
        print(f"Repo ID: {repo.get('id')}")
        print(f"Discussions enabled: {repo.get('hasDiscussionsEnabled')}")
        for cat in repo.get("discussionCategories", {}).get("nodes", []):
            print(f"Category: {cat['name']} | ID: {cat['id']}")
except urllib.error.HTTPError as e:
    print(f"GraphQL error {e.code}: {e.read().decode()}")

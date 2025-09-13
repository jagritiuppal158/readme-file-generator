
import os
import base64
import requests
import io
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)

GITHUB_API = "https://api.github.com"

def parse_github_url(url: str):
    import re
    if url.startswith("git@"):
        m = re.search(r"git@[^:]+:([^/]+)/(.+?)(?:\.git)?$", url)
    else:
        m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?(?:/|$)", url)
    if not m:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return m.group(1), m.group(2)


def gh_get(path: str, token: str = None, params: dict = None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.get(GITHUB_API + path, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r


def fetch_repo_metadata(owner, repo, token=None):
    return gh_get(f"/repos/{owner}/{repo}", token).json()


def fetch_readme(owner, repo, token=None):
    try:
        r = gh_get(f"/repos/{owner}/{repo}/readme", token)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise
    data = r.json()
    if "content" in data and data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None
    return None


def fetch_topics(owner, repo, token=None):
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"{GITHUB_API}/repos/{owner}/{repo}/topics"
    r = requests.get(url, headers=h)

#!/usr/bin/env python3
"""
Clone a GitOps repo, update configs/<service>/<environment>/values.yaml
to set image.tag, then commit (non-prod) or PR (prod).

Usage:
  python image_updater.py \
    --repo-url     https://github.com/ORG/GITOPS.git \
    --service      ai-server \
    --environment  dev \
    --tag          dev-abc1234
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from github import Github       # pip install PyGithub
import yaml                     # pip install PyYAML

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)


def update_values(base_dir, service, env, tag):
    vals = Path(base_dir) / "configs" / service / env / "values.yaml"
    if not vals.exists():
        logging.error(f"Missing values file: {vals}")
        sys.exit(1)
    data = yaml.safe_load(vals.read_text())
    data.setdefault("image", {})["tag"] = tag
    vals.write_text(yaml.dump(data, sort_keys=False))
    logging.info(f"Set image.tag={tag} in {vals}")


def main():
    parser = argparse.ArgumentParser(
        description='Clone GitOps repo, update image tag, push or PR.'
    )
    parser.add_argument("--repo-url",    required=True, help="GitOps repo HTTPS URL")
    parser.add_argument("--service",     required=True, help="Microservice name")
    parser.add_argument("--environment", required=True,
                        choices=["dev", "staging", "prod"], help="Target env")
    parser.add_argument("--tag",         required=True, help="New image tag")
    args = parser.parse_args()

    token = os.getenv("GITOPS_PAT")
    if not token:
        logging.error("GITOPS_PAT not set")
        sys.exit(1)

    # Build an auth-URL so both clone and push use your PAT
    auth_url = args.repo_url.replace(
        "https://",
        f"https://x-access-token:{token}@"
    )

    # derive owner/repo from URL for PyGithub
    parsed = urlparse(args.repo_url)
    repo_full = parsed.path.lstrip("/").removesuffix(".git")

    # authenticate GitHub API
    gh = Github(token)
    repo = gh.get_repo(repo_full)
    main_branch = repo.default_branch

    is_prod = (args.environment == "prod")
    branch = main_branch if not is_prod else f"update-{args.service}-{args.tag}"

    with tempfile.TemporaryDirectory() as tmp:
        logging.info(f"Cloning {args.repo_url}")
        run(f"git clone {auth_url} .", cwd=tmp)

        if is_prod:
            logging.info(f"Creating branch {branch}")
            run(f"git checkout -b {branch} origin/{main_branch}", cwd=tmp)
        else:
            run(f"git checkout {main_branch}", cwd=tmp)

        # set Git identity
        run('git config user.name "github-actions"', cwd=tmp)
        run('git config user.email "actions@github.com"', cwd=tmp)

        # update the values file
        update_values(tmp, args.service, args.environment, args.tag)

        # commit
        run("git add .", cwd=tmp)
        msg = f"ci: update {args.service} {args.environment} tag to {args.tag}"
        run(f'git commit -m "{msg}"', cwd=tmp)

        # push with auth
        logging.info(f"Pushing changes to {branch}")
        run(f"git push {auth_url} {branch}", cwd=tmp)

        # open PR for prod
        if is_prod:
            logging.info("Opening pull request")
            pr = repo.create_pull(
                title=msg,
                body="Automated image-tag update",
                head=branch,
                base=main_branch
            )
            logging.info(f"✅ PR created: {pr.html_url}")
        else:
            logging.info("✅ Changes committed directly to main")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse, os, sys
from urllib.parse import urlparse
from github import Github
import yaml

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-url",     required=True,
                   help="HTTPS URL of the GitOps repo")
    p.add_argument("--service",      required=True)
    p.add_argument("--environment",  required=True)
    p.add_argument("--tag",          required=True)
    args = p.parse_args()

    token = os.getenv("GITHUB_PAT")
    if not token:
        print("❌ GITHUB_PAT is required", file=sys.stderr)
        sys.exit(1)

    # Parse owner/repo from URL
    parsed = urlparse(args.repo_url)
    repo_full = parsed.path.lstrip("/").removesuffix(".git")

    gh   = Github(token)
    repo = gh.get_repo(repo_full)
    default_branch = repo.default_branch

    # For prod, create a feature branch; otherwise update main directly
    if args.environment == "prod":
        branch_name = f"update-{args.service}-{args.environment}-{args.tag}"
        src = repo.get_git_ref(f"heads/{default_branch}")
        repo.create_git_ref(f"refs/heads/{branch_name}", src.object.sha)
        target_branch = branch_name
    else:
        target_branch = default_branch

    # Load and modify values.yaml
    path = f"configs/{args.service}/{args.environment}/values.yaml"
    contents = repo.get_contents(path, ref=target_branch)
    data = yaml.safe_load(contents.decoded_content)

    data.setdefault("image", {})
    data["image"]["tag"] = args.tag
    new_yaml = yaml.dump(data, sort_keys=False)

    commit_msg = f"ci: update {args.service} {args.environment} image tag to {args.tag}"
    repo.update_file(
        path=path,
        message=commit_msg,
        content=new_yaml,
        sha=contents.sha,
        branch=target_branch
    )

    # If prod, open a PR; else just print success
    if args.environment == "prod":
        pr = repo.create_pull(
            title=commit_msg,
            body="Please review and merge to apply the image update.",
            head=branch_name,
            base=default_branch
        )
        print(f"✅ Created pull request: {pr.html_url}")
    else:
        print(f"✅ Committed {path} on branch {target_branch}")

if __name__ == "__main__":
    main()

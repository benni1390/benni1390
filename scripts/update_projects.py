#!/usr/bin/env python3

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


README = Path(__file__).resolve().parents[1] / "README.md"
START_MARKER = "<!-- projects:start -->"
END_MARKER = "<!-- projects:end -->"
PAGE_SIZE = 100


def get_repositories(username):
    repositories = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?type=owner&per_page={PAGE_SIZE}&page={page}"
        )
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "update-profile-projects",
            },
        )
        with urlopen(request, timeout=30) as response:
            page_repositories = json.load(response)

        repositories.extend(page_repositories)
        if len(page_repositories) < PAGE_SIZE:
            break
        page += 1

    return sorted(
        (
            repository
            for repository in repositories
            if not repository["private"]
            and repository["owner"]["login"].casefold() == username.casefold()
            and repository["name"].casefold() != username.casefold()
        ),
        key=lambda repository: repository["name"].casefold(),
    )


def update_readme(username):
    readme = README.read_text(encoding="utf-8")
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise ValueError("README.md must contain one projects start and end marker")

    repositories = get_repositories(username)
    if not repositories:
        raise ValueError(f"No public repositories found for {username}")

    project_list = "\n".join(
        f"- [**{repository['name']}**]({repository['html_url']})"
        + (f" - {repository['description']}" if repository["description"] else "")
        for repository in repositories
    )
    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    updated_readme = f"{readme[:start]}\n{project_list}\n{readme[end:]}"

    if updated_readme != readme:
        README.write_text(updated_readme, encoding="utf-8")


if __name__ == "__main__":
    update_readme(os.environ.get("GITHUB_USER", "benni1390"))

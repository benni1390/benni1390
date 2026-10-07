GITHUB_USER ?= benni1390

.DEFAULT_GOAL := update-projects

update-projects:
	GITHUB_USER="$(GITHUB_USER)" python3 scripts/update_projects.py

.PHONY: update-projects

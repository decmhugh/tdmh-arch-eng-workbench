#!/usr/bin/env bash
# Assemble mkdocs-content/ directory from repo sources.
# Uses symlinks locally, copies in CI (Jenkins may not support symlinks in all contexts).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTENT_DIR="${REPO_ROOT}/mkdocs-content"

# Clean previous build
rm -rf "${CONTENT_DIR}"
mkdir -p "${CONTENT_DIR}"

# Determine link mode: symlink locally, copy in CI
if [[ "${CI:-}" == "true" || "${JENKINS_URL:-}" != "" ]]; then
    link() { cp -r "$1" "$2"; }
else
    link() { ln -s "$1" "$2"; }
fi

# Home page
link "${REPO_ROOT}/scripts/mkdocs-index.md" "${CONTENT_DIR}/index.md"

# Capability map (living document)
link "${REPO_ROOT}/docs/capability-map.md" "${CONTENT_DIR}/capability-map.md"

# Assurance register (generated from references/assurance-records.yaml)
link "${REPO_ROOT}/docs/assurance-records.md" "${CONTENT_DIR}/assurance-records.md"

# Process docs
link "${REPO_ROOT}/docs/process" "${CONTENT_DIR}/process"

# Reference material (regulatory guidelines)
link "${REPO_ROOT}/docs/reference" "${CONTENT_DIR}/reference"

# Specs
link "${REPO_ROOT}/specs" "${CONTENT_DIR}/specs"

# Templates
link "${REPO_ROOT}/docs/templates" "${CONTENT_DIR}/templates"

echo "mkdocs-content/ assembled from repo sources."

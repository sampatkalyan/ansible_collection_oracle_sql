# Guide: Dev Containers Setup & Ansible Galaxy Publishing

This document provides a complete, step-by-step educational guide so you can understand, maintain, and execute these workflows on your own without needing an AI assistant.

---

# Part 1: Docker & Dev Containers for Ansible Collections

## Why Containerized Development?

When developing Ansible collections on Windows, you inevitably run into two roadblocks:
1. **Linux-Only Dependencies**: Ansible controller code (`ansible.module_utils.basic`) imports Unix-only libraries (`grp`, `fcntl`, `pwd`). Windows cannot run these natively.
2. **Collection Namespace Requirements**: Ansible expects collections to reside inside `ansible_collections/<namespace>/<collection_name>`. In a standalone Git repo, this directory hierarchy doesn't exist on disk, causing IDEs like Pylance to show "Cannot find module" errors.

## How VS Code Dev Containers Solve This

A Dev Container allows VS Code on Windows to use a Docker container as its development environment. Your source files stay on your Windows hard drive, but VS Code executes all terminals, linters, Python interpreters, and test tools inside Linux.

### The Two Core Files in `.devcontainer/`

```text
.devcontainer/
├── Dockerfile          # Defines the Linux environment & dependencies
└── devcontainer.json   # Configures VS Code mount points and extensions
```

### 1. The `devcontainer.json` Trick for Ansible Collections
In `devcontainer.json`, notice how the workspace mount is configured:

```json
{
  "workspaceMount": "source=${localWorkspaceFolder},target=/workspaces/ansible_collections/sampatkalyan/oracle_sql,type=bind",
  "workspaceFolder": "/workspaces/ansible_collections/sampatkalyan/oracle_sql"
}
```

**Why this is crucial:**
- Instead of mounting your project at `/workspaces/oracle_sql`, it mounts directly into the canonical Ansible path `/workspaces/ansible_collections/sampatkalyan/oracle_sql`.
- We then set `PYTHONPATH=/workspaces` and `ANSIBLE_COLLECTIONS_PATH=/workspaces`.
- **Result**: `from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import ...` works natively with zero squiggly lines and zero manual symlink hacks!

---

## How to Use It (Step-by-Step)

### Prerequisites:
1. **Docker Desktop** installed and running on Windows.
2. The **"Dev Containers"** extension installed in VS Code (`ms-vscode-remote.remote-containers`).

### Launching:
1. Open the project in VS Code on Windows.
2. Press **`F1`** (or `Ctrl+Shift+P`) to open the Command Palette.
3. Type and select: **`Dev Containers: Reopen in Container`**.
4. VS Code builds the image (only takes ~1–2 minutes the first time, then caches it).
5. Once inside, you have an integrated Linux terminal where you can run:
   ```bash
   pytest tests/ -v
   ansible-test units --docker
   ansible-test sanity --docker
   ```

---

# Part 2: Publishing the Collection to Ansible Galaxy

## 1. Prerequisites Checklist

Before publishing to Galaxy, ensure you have:
1. **An Ansible Galaxy Account**: Log in at [galaxy.ansible.com](https://galaxy.ansible.com/) (using your GitHub login).
2. **Namespace Ownership**: Verify that the `sampatkalyan` namespace exists under your Galaxy profile.
3. **Your Galaxy API Key**:
   - Go to [galaxy.ansible.com/ui/token/](https://galaxy.ansible.com/ui/token/) (or click your Avatar → **Preferences** / **API Key**).
   - Click **Show API Key** and copy the token.

---

## 2. Choosing the Version Number

In `galaxy.yml`, the current version is:
```yaml
version: 0.0.1
```

Because these changes are **backward-compatible maintenance fixes, documentation corrections, and security updates**, standard Semantic Versioning (SemVer) dictates bumping the **PATCH** version:

```yaml
version: 0.0.2
```
*(Or `0.1.0` if you consider the documentation rewrite and tests restructure a minor milestone).*

---

## 3. Files to Update Before Publishing

### Step A: Update `galaxy.yml`
Change line 3:
```yaml
version: 0.0.2
```

### Step B: Update `CHANGELOG.md`
Change `## [Unreleased]` to:
```markdown
## [0.0.2] - 2026-11-06

### Added
...
### Changed
...
### Fixed
...
### Security
...
```

---

## 4. The Exact Commands to Build and Publish

Run these commands inside your terminal (or inside the Dev Container):

### Step 1: Build the collection artifact
```bash
ansible-galaxy collection build --force
```
This reads `galaxy.yml` and packages the repository into a distributable archive:
`sampatkalyan-oracle_sql-0.0.2.tar.gz`

### Step 2: Publish to Galaxy
```bash
ansible-galaxy collection publish ./sampatkalyan-oracle_sql-0.0.2.tar.gz --api-key <YOUR_GALAXY_API_KEY>
```

Ansible Galaxy will upload the tarball, run automated import checks, and publish the release. You will receive an import status URL in the terminal output to monitor progress.

---

## 5. (Optional) Git Tagging & Release

Once published to Galaxy, tag the release in Git so your Git history matches Galaxy:

```bash
git checkout main
git merge maintenance/fixes
git tag -a v0.0.2 -m "Release version 0.0.2: Namespace normalization, documentation, and security audit"
git push origin main --tags
```


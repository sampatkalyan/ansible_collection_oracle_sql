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



---

# Part 3: Deep Dive — GitHub Actions, CI/CD Architecture & Secret Security

## 1. How GitHub Actions Works Under the Hood

GitHub Actions is an automation platform built directly into GitHub. It works via three core concepts:

1. **Workflows (`.github/workflows/*.yml`)**:
   YAML files defining what should run, when, and where.
2. **Triggers (`on:`)**:
   - `push: tags: ['v*']`: Runs automatically whenever you push a Git tag like `v0.0.2`.
   - `workflow_dispatch:`: Adds a manual **"Run workflow"** button in the GitHub UI, and allows programmatic execution via the CLI (`gh workflow run release.yml`).
3. **Hosted Runners (`runs-on: ubuntu-latest`)**:
   GitHub spins up a fresh, ephemeral Ubuntu Linux virtual machine in Microsoft Azure for each job. When the job finishes, the VM is immediately destroyed.

---

## 2. Why Storing Credentials in GitHub Secrets is the Gold Standard

Never hardcode API keys, passwords, or tokens in scripts, commit messages, or chat conversations. GitHub Secrets provides defense-in-depth through five security pillars:

### A. Asymmetric Encryption at Rest (NaCl / Libsodium)
When you paste your token into GitHub Secrets, GitHub encrypts it immediately in your browser using public-key cryptography (libsodium Box algorithm). GitHub's servers only hold the encrypted ciphertext; only the ephemeral runner VM spun up during your workflow run has the temporary key to decrypt it.

### B. Automatic Runtime Log Masking
GitHub Actions inspects all stdout and stderr streams in real-time. If any step prints the decrypted value of a secret, GitHub automatically replaces it with `***` (as seen in our release logs: `GALAXY_API_KEY: ***`). Even if a command accidentally echoes the token, it will never appear in web logs.

### C. Safe Injection via Environment Variables
Instead of passing sensitive tokens directly in the shell command line:
```bash
# BAD: Visible in process table (ps -ef)
ansible-galaxy collection publish ... --api-key "my-secret-token"
```
The workflow injects it as an environment variable into the process:
```yaml
env:
  GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
run: ansible-galaxy collection publish ... --api-key "$GALAXY_API_KEY"
```

### D. Zero-Trust for AI Assistants & Collaborators
By keeping the secret in GitHub:
- You never have to copy-paste your sensitive token into an AI chat or prompt.
- The AI can write, inspect, and trigger the workflow pipeline without ever reading or knowing the token value.
- Pull requests from external forks do not have access to your repository secrets, preventing malicious PRs from stealing your keys.

---

## 3. Galaxy Import Validation Lessons (Gotchas Learned in v0.0.2)

When Galaxy imports a new collection version, it runs rigorous automated checks:

1. **SPDX License Identifiers**:
   - `license:` in `galaxy.yml` cannot be freeform text like `Apache License 2.0`.
   - It must be the official SPDX identifier: `Apache-2.0` (or `GPL-3.0-or-later`, `MIT`, etc.).
2. **`meta/runtime.yml` is Mandatory**:
   - Galaxy requires a `meta/runtime.yml` file declaring `requires_ansible: '>=2.15.0'`. Without this, Galaxy import fails with `Code: UNKNOWN`.
3. **Every Module Must Have a `DOCUMENTATION` String**:
   - Galaxy executes `ansible-doc` on every Python file in `plugins/modules/`.
   - If a file (such as `oraclesql_user.py`) lacks a `DOCUMENTATION` block, the entire collection import is rejected.
4. **Module Name in `DOCUMENTATION`**:
   - In the YAML frontmatter of `DOCUMENTATION = '''...'''`, `module: <name>` must be the short name (`module: oraclesql_database`), NOT the full FQCN (`sampatkalyan.oracle_sql.oraclesql_database`).

---

## 4. Useful GitHub CLI (`gh`) Commands for Workflows

You can trigger and inspect your workflows directly from your terminal:

```bash
# Trigger a workflow run:
gh workflow run release.yml --ref main

# List recent runs:
gh run list --workflow=release.yml

# Watch or view a specific run:
gh run view <RUN_ID>

# View only the failed steps of a run:
gh run view <RUN_ID> --log-failed
```

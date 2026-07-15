# repo-skeleton

An **agent-agnostic** starter repo. It ships one canonical set of agent
instructions + a self-contained coding-standards gate, so Claude, Codex, Gemini,
and Copilot all follow the same rules with no per-tool restating.

## Start a new project from this skeleton

Bitbucket has no one-click "template" button (that's a GitHub feature), so copy
from this skeleton:

```bash
git clone <this-skeleton-url> my-new-project
cd my-new-project
rm -rf .git && git init            # detach from the skeleton's history
```

Use `git clone` (not `cp -r`) so the symlinks are preserved as symlinks. On
Windows, enable `git config --global core.symlinks true`.

## Then, once per new project

1. **Rename the project skill:** `.agents/skills/project-guide/` → something
   specific (e.g. `myapp-maintainer`), update its `name:` frontmatter, and fill
   in the TODOs. Keep it updated as the project evolves — it's the repo's memory
   for every agent.
2. **Wire the linter deps:** merge `requirements-dev.txt` (`ruff`, `pre-commit`)
   into your project's real manifest.
3. **Install the gate:** `pip install pre-commit && pre-commit install`.
4. **Adjust exceptions:** add this repo's vendored/generated dirs to the
   `extend-exclude` in `ruff.toml` and the `exclude:` regex in
   `.pre-commit-config.yaml`. Grandfather any existing backlog via
   `[lint.per-file-ignores]` in `ruff.toml` (see the commented example there).

## Layout

```
AGENTS.md                         canonical, repo-agnostic agent entrypoint
CLAUDE.md            -> AGENTS.md  (symlink)
.github/copilot-instructions.md -> ../AGENTS.md  (symlink)

.agents/skills/                   source of truth for skills (Agent Skills spec)
  project-guide/                  governing skill for THIS repo (placeholder)
  coding-standards/               house style (guidance only)
.claude/skills       -> ../.agents/skills  (symlink, so Claude discovers them)

linting/                          the machinery (kept out of the skills)
  ruff.toml  check.py  standards_checks/  eslint.config.mjs  .pre-commit-config.yaml

ruff.toml                         extends linting/ruff.toml + repo exceptions
.pre-commit-config.yaml           runs ruff + linting/check.py at commit time
```

**Why it's agent-agnostic:** enforcement (pre-commit → ruff +50/250 line
checks) runs at the git layer, so it holds regardless of which agent commits;
guidance is one canonical `AGENTS.md` + symlinks, so each tool reads it via its
native entrypoint without restating anything.

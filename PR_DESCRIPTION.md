PR: Fix CI/CD and Terraform workflows

Summary

This PR centralizes multiple fixes to GitHub Actions workflows to remove warnings, fix invalid contexts, and harden CI/CD pipelines for AWS/Terraform/ECS ops.

Files changed (high level)

- .github/workflows/terraform-plan.yml
- .github/workflows/terraform-apply.yml
- .github/workflows/rollback-ecs.yml
- .github/workflows/deploy-ecs.yml
- .github/workflows/workflow-lint.yml (new)
- SECRETS_REQUIRED.md (new)

What I fixed

- Replaced invalid GitHub expression usages and ensured `env` variables are defined via `$GITHUB_ENV` before use.
- Replaced Python heredoc blocks in workflows with `jq` to parse `tfplan.metadata.json` (avoids YAML parsing issues).
- Standardized `SHORT_SHA` creation and `ENV` handling.
- Replaced complex/unsupported inline GitHub expressions in `env` with shell fallbacks for inputs vs secrets (e.g. `rollback-ecs.yml`).
- Added a `workflow-lint` job to run `yamllint` and `shellcheck` on workflow shell blocks.
- Added `SECRETS_REQUIRED.md` and a copy-paste file with required secrets.

Testing notes

- I validated YAML structure and removed constructs that cause "Context access might be invalid" warnings.
- I could not run Actions in this environment; please run the `Lint Workflows` workflow by opening a PR or pushing the branch to validate in CI.

Next steps (recommended)

1. Add the required secrets (see `SECRETS_REQUIRED.md`).
2. Create a feature branch, commit these changes, push and open a PR to run `workflow-lint` automatically.
3. If lint finds issues, address them; I can iterate on fixes.

Commands to create branch and PR locally

```bash
git checkout -b fix/workflows
git add .
git commit -m "Fix workflows: terraform, ecs, lint"
git push origin fix/workflows
# Then open PR on GitHub UI or use `gh`:
# gh pr create --fill --base main --head fix/workflows
```

If you want, I can prepare and open the PR for you (requires repository push access).
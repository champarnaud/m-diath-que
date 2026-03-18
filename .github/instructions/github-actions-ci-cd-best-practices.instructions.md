---
applyTo: '.github/workflows/*.yml,.github/workflows/*.yaml'
description: 'Comprehensive guide for building robust, secure, and efficient CI/CD pipelines using GitHub Actions. Covers workflow structure, jobs, steps, environment variables, secret management, caching, matrix strategies, testing, and deployment strategies.'
---
# GitHub Actions CI/CD Best Practices

## Workflow Structure

- Use descriptive `name` fields for workflows, jobs, and steps.
- Choose appropriate triggers (`push`, `pull_request`, `workflow_dispatch`, `schedule`).
- Use `paths` and `branches` filters to avoid unnecessary runs.
- Define workflow-level `permissions` — default to `contents: read`.
- Add `concurrency` groups to cancel outdated runs on the same branch.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Security Best Practices

- **Never hardcode** secrets, tokens, or credentials in workflow files.
- Store sensitive values in **GitHub Secrets** (`${{ secrets.MY_SECRET }}`).
- Use **OIDC** for cloud authentication (AWS, Azure, GCP) — no long-lived credentials.
- Default `GITHUB_TOKEN` permissions to `contents: read`; grant additional permissions explicitly and minimally.
- Pin third-party actions to a **full commit SHA** (not a floating tag) to prevent supply-chain attacks.

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

- Integrate dependency review (`actions/dependency-review-action`) on PRs.
- Run SAST scanning (e.g., CodeQL) on every push to default branch and PRs.
- Treat `pull_request_target` with extreme caution — never check out untrusted code in that context running privileged steps.

## Caching and Performance

- Cache dependencies using `actions/cache` with a `key` based on `hashFiles(...)`.
- Use `restore-keys` as fallback for partial cache hits.
- Set `fetch-depth: 1` for `actions/checkout` unless full history is required.
- Use `strategy.matrix` to parallelize builds across OS versions, language versions, etc.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Environment Variables

- Define env vars at the lowest necessary scope (step > job > workflow).
- Use `${{ vars.MY_VAR }}` for non-sensitive configuration values (repository/environment variables).
- Avoid interpolating secrets directly into `run` commands; use environment injection.

```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

## Testing

### Unit Tests
- Dedicated job, runs on every push and PR.
- Fail fast: run linting/static analysis before unit tests.
- Upload test results as artefacts for debugging failed runs.
- Track test coverage; fail if coverage drops below threshold.

### Integration Tests
- Use `services` containers for database, cache, or message-broker dependencies.
- Run against a clean, ephemeral environment.

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Deployment

- Use **GitHub Environments** with required reviewers for staging and production gates.
- Always have a rollback plan: document the rollback step or automate it.
- Add post-deployment health checks (smoke tests, HTTP probes).
- Use deployment concurrency locks to prevent simultaneous production deploys.

```yaml
environment:
  name: production
  url: https://example.com
```

## Reusability

- Extract repeated logic into **reusable workflows** (`workflow_call`) or **composite actions**.
- Store shared actions in a dedicated internal repository.
- Version reusable workflows with tags.

## Notifications and Observability

- Notify on failure via Slack, Teams, or email using dedicated actions.
- Always upload logs, test reports, and build artefacts for post-mortem analysis.
- Set meaningful `timeout-minutes` on jobs to prevent hung runners.

## Checklist

- [ ] Workflow name and triggers are appropriate
- [ ] `permissions` are minimal and explicit
- [ ] Third-party actions pinned to commit SHA
- [ ] No secrets hardcoded; OIDC used for cloud auth
- [ ] Dependency and SAST scanning in place
- [ ] Caching configured for dependencies
- [ ] Tests run on every PR; coverage enforced
- [ ] Deployment uses GitHub Environments with approvals
- [ ] Rollback procedure documented or automated
- [ ] Artefacts and logs uploaded on failure

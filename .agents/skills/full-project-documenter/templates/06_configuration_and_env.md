# [Project Name] — Configuration, Environment & Secrets Reference

> **Document ID**: `06_CONFIGURATION_AND_ENV`  
> **Classification**: Operational Configuration Catalog  
> **Mandate**: Catalog 100% of environment variables, config files, flags, and secret requirements.

---

## 1. Environment Variables Encyclopedia

| Variable Name | Required? | Default Value | Example Value | Description & Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `NODE_ENV` / `ENV` | Yes | `development` | `production` | Runtime mode (`development`, `staging`, `production`, `test`). |
| `PORT` | No | `8080` | `3000` | TCP port the web server binds to. |
| `DATABASE_URL` | Yes | - | `postgresql://user:pass@localhost:5432/db` | Connection string for primary relational database. |
| `REDIS_URL` | No | `redis://127.0.0.1:6379/0` | `rediss://...` | Connection URI for cache and rate limiter. |
| `JWT_SECRET` | Yes | - | `[64-char-hex]` | Secret key used for signing and verifying JSON Web Tokens. |

---

## 2. Configuration Files & Schemas

| Config File | Format | Scope / Stage | Description |
| :--- | :--- | :--- | :--- |
| `tsconfig.json` | JSON with Comments | Compilation | TypeScript strictness, target ES version, path aliases. |
| `docker-compose.yml` | YAML | Local Dev | Orchestrates local DB, Redis, and mock service containers. |
| `.env.example` | Key-Value | Template | Starter template for developer local environments. |

---

## 3. Secrets Management & Rotation Policy

- **Storage Engine**: [e.g. AWS Secrets Manager, HashiCorp Vault, Doppler, GCP Secret Manager]
- **Rotation Frequency**: [e.g. 90-day rotation on database credentials and API keys]
- **Zero-Commit Guardrails**: Git pre-commit hooks (`gitleaks`, `trufflehog`) prevent accidental commits of keys.

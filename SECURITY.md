# Security Policy

## Secrets

Do not commit `.env` files, credentials, tokens, customer data, or database exports. Use `.env.example` only for variable names and keep real values outside version control.

If a secret is committed, revoke or rotate it immediately. Removing the value in a later commit does not remove it from Git history.

## Data Handling

The repository accepts only synthetic or explicitly public data. Raw personal data must not be used. The optional LLM integration sends aggregated KPI values only, but users remain responsible for reviewing the provider's policies.

## Reporting a Vulnerability

Open a private security advisory in the Git hosting platform rather than posting credentials or sensitive evidence in a public issue.


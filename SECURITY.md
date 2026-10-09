# Security Policy

## Scope

This repository is a sanitized portfolio edition of an internal healthcare analytics application. It must never contain production credentials, patient information, internal network addresses, session databases, private keys, production exports or production logs.

## Supported code

Security fixes are applied to the latest version on the `main` branch.

## Reporting a vulnerability

Do not open a public issue containing credentials, patient information, infrastructure details or exploitable security data.

Use GitHub's private security reporting feature when available. If private reporting is unavailable, contact the repository owner through a private channel.

## Security controls represented in the project

The application architecture includes:

- read-only Oracle integration;
- local application authentication;
- role-based access control;
- session expiration;
- CSRF validation for state-changing operations;
- password hashing using `scrypt`;
- authentication and administrative audit events;
- restricted CORS configuration;
- environment-based secrets;
- bounded application caching;
- explicit limits for large analytical endpoints.

## Repository hygiene

The repository excludes:

- `.env` and environment-specific secret files;
- local authentication databases;
- Oracle credentials;
- private keys and certificates;
- generated exports;
- build artifacts;
- caches;
- backups;
- production logs.

Before publishing a release, run secret scanning and verify that all sample configuration values are non-production placeholders.

## Deployment note

Production deployments should terminate TLS at a trusted reverse proxy and enable secure cookies. Demo settings such as `APP_SECURE_COOKIES=false` are intended only for local HTTP development.

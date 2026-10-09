# Portfolio Demo

This public demo runs with deterministic synthetic data and does not require an Oracle connection.

## Local

```bash
cd frontend
npm ci
npm run demo
```

Open `http://localhost:4173`.

## Docker

```bash
docker compose -f docker-compose.demo.yml up --build
```

Open `http://localhost:8080`.

## Suggested walkthrough

1. Resumo integrado
2. Recebimentos
3. Contas e pacientes
4. Glosas e pendências
5. Análises

All people, accounts, financial events and values in demo mode are fictional and exist only to demonstrate the application flow.

# Backend: Seeding Providers and Gathering News

## Prerequisites

Run all commands from the project root (the directory containing `Backend/`).

Activate your virtual environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Make sure your database configuration is correct and the database is accessible.

## 1. Seed Providers

Run:

```powershell
python -m Backend.seed_providers
```

**What it does:**

- Reads provider information from the configured mock source data.
- Checks which providers already exist.
- Creates missing provider records.
- Commits changes to the database.

This command does not fetch news articles or automatically store RSS source records.

## 2. Gather News

Run:

```powershell
python -m Backend.run_news_gathering
```

**What it does:**

1. Loads active news sources.
2. Fetches and parses RSS feeds.
3. Normalizes article data into a consistent format.
4. Creates or updates articles through the services and repositories.
5. Commits database changes as configured.

Example output:

```text
Fetching source: NOS Algemeen RSS
Fetched 25 articles
created: Example news headline
updated: Another news headline
```

## Troubleshooting

- **`ModuleNotFoundError`:** Run commands from the project root.
- **Database errors:** Check your database configuration and connection.
- **RSS failures:** Verify the feed URL and inspect parsing warnings.

**Note:** News gathering can modify the database. Ensure you are using the intended environment before running it.

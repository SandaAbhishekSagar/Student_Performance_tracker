# Worker Count Fix

## Problem
Gunicorn is booting an excessive number of workers (98+), which is causing resource issues and continuous restarting.

## Solution Applied

1. **Capped Worker Count**: Updated `gunicorn_config.py` to limit workers to a maximum of 16 (with default of 8)
2. **Disabled Preload**: Changed `preload_app = False` to avoid database connection issues with multiple workers
3. **Fixed Worker Calculation**: Ensured worker count is reasonable and capped

## Changes Made

### gunicorn_config.py
- Worker count now capped at 8 by default (max 16)
- Formula: `min(cpu_count * 2 + 1, 8)`
- `preload_app = False` to avoid database connection issues

## How to Apply

### Option 1: Rebuild Docker Image (Recommended)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Option 2: Set Environment Variable
Add to your `.env` file to override worker count:
```bash
GUNICORN_WORKERS=4
```

Then restart:
```bash
docker-compose restart
```

## Verification

After applying the fix, check logs:
```bash
docker-compose logs -f web
```

You should see:
- Only 4-8 workers booting (not 98+)
- Workers staying up (not continuously restarting)
- Application responding normally

## Recommended Worker Count

For this application:
- **Small deployment**: 2-4 workers
- **Medium deployment**: 4-8 workers  
- **Large deployment**: 8-16 workers (max)

Set via environment variable:
```bash
GUNICORN_WORKERS=4
```


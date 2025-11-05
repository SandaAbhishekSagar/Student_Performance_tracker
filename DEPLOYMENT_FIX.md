# Deployment Fix - Missing psycopg2 Module

## Problem
The application is trying to connect to PostgreSQL but the `psycopg2` module is not installed, causing the error:
```
ModuleNotFoundError: No module named 'psycopg2'
```

## Solution

### Option 1: Rebuild Docker Image (Recommended)
The `requirements.txt` has been updated to include `psycopg2-binary`. Rebuild your Docker image:

```bash
# Stop current containers
docker-compose down

# Rebuild with updated dependencies
docker-compose build --no-cache

# Start again
docker-compose up -d
```

### Option 2: Use SQLite Instead (Quick Fix)
If you want to use SQLite instead of PostgreSQL, update your `.env` file:

```bash
# In your .env file, change DATABASE_URL to:
DATABASE_URL=sqlite:///instance/student_tracker.db
```

Then restart:
```bash
docker-compose restart
```

### Option 3: Install Manually in Running Container (Not Recommended)
If you need to fix a running container without rebuilding:

```bash
# Enter the container
docker-compose exec web bash

# Install psycopg2-binary
pip install psycopg2-binary==2.9.9

# Exit and restart
exit
docker-compose restart
```

## Verification

After applying the fix, check the logs:
```bash
docker-compose logs -f web
```

You should see the application starting successfully without the `psycopg2` error.

## Prevention

The `requirements.txt` file now includes `psycopg2-binary==2.9.9`, so future deployments will automatically include the PostgreSQL driver.


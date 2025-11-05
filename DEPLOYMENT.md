# Deployment Guide

## Database Setup

### ✅ **No Manual Database Setup Required!**

The application **automatically initializes the database** on first startup. You don't need to set up the database manually.

### How It Works

1. **SQLite (Default)**: The database file is automatically created in the `instance/` directory on first run
2. **PostgreSQL/MySQL**: Tables are automatically created when the app starts if they don't exist
3. **Initialization**: The `init_db()` function runs automatically on startup

### What Happens on First Run

- ✅ Database tables are created automatically
- ✅ Demo teacher account is created (if no teachers exist)
- ✅ Ready to use immediately

### Database Location

- **SQLite**: `instance/student_tracker.db` (created automatically)
- **PostgreSQL/MySQL**: Tables created in the configured database

### Manual Database Initialization (Optional)

If you need to manually initialize the database:

```bash
# Using Python
python -c "from app import init_db; init_db()"

# Or using Docker
docker-compose exec web python -c "from app import init_db; init_db()"
```

### For Production (PostgreSQL/MySQL)

1. **Set up database server** (PostgreSQL/MySQL)
2. **Update `.env` file** with database connection string:
   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/student_tracker
   ```
3. **Deploy application** - tables will be created automatically on first run

### Troubleshooting

**Database not initializing?**
- Check file permissions on `instance/` directory
- Check database connection string in `.env`
- Check application logs for errors

**Reset database:**
```bash
# SQLite
rm instance/student_tracker.db
# Restart application - database will be recreated

# PostgreSQL/MySQL
# Drop and recreate database, then restart app
```


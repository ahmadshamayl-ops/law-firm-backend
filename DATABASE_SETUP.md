# PostgreSQL Database Setup Guide

## Prerequisites
- PostgreSQL installed and running
- pgAdmin 4 installed
- Database `law_firm` created in PostgreSQL (or use your DB_NAME)

## Step 1: Create Database in pgAdmin

1. Open pgAdmin 4
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database..."
4. Set the database name: Use the value from your `DB_NAME` environment variable (default: `law_firm`)
5. Click "Save"

## Step 2: Configure Environment Variables

Create a `.env` file in the project root with your database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=law_firm
DB_USER=postgres
DB_PASSWORD=your_password_here
```

**Replace the values with your actual PostgreSQL configuration:**
- `DB_HOST`: PostgreSQL server host (usually `localhost` or `127.0.0.1`)
- `DB_PORT`: PostgreSQL port (default is `5432`)
- `DB_NAME`: Database name (should be `law_firm` or your custom name)
- `DB_USER`: PostgreSQL username (usually `postgres`)
- `DB_PASSWORD`: Your PostgreSQL password

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Test Database Connection

You can test the connection by running:

```bash
python app/init_db.py
```

This will:
- Connect to your PostgreSQL database
- Create the `users` table if it doesn't exist
- Display success message if connection is successful

## Step 5: Verify in pgAdmin

1. In pgAdmin, expand your database (from `DB_NAME`)
2. Expand "Schemas" → "public" → "Tables"
3. You should see the `users` table with columns:
   - `username` (Primary Key, VARCHAR(50))
   - `email` (Unique, VARCHAR(100))
   - `full_name` (VARCHAR(100))
   - `hashed_password` (VARCHAR(255))
   - `created_at` (TIMESTAMP)

## Step 6: Start the Application

```bash
uvicorn app.main:app --reload
```

The tables will be created automatically on startup if they don't exist.

## Troubleshooting

### Connection Error: "could not connect to server"
- Verify PostgreSQL is running
- Check `DB_HOST` and `DB_PORT` in `.env` file
- Ensure PostgreSQL service is started

### Authentication Failed
- Verify `DB_USER` and `DB_PASSWORD` are correct
- Check PostgreSQL user permissions

### Database Does Not Exist
- Create the database in pgAdmin first
- Ensure `DB_NAME` matches the actual database name

### Table Already Exists
- The script will not recreate existing tables
- To reset, drop the table in pgAdmin and run `init_db.py` again

### Port Already in Use
- Check if another PostgreSQL instance is using the port
- Verify `DB_PORT` matches your PostgreSQL configuration

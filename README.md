# HR Employee Search Microservice

A lightweight employee search API built with Python's standard library only (no external dependencies). Features include advanced search filtering, rate limiting, and support for millions of employee records.

## Features

- 🔍 **Advanced Search**: Filter by status, location, company, department, and position
- 🚦 **Rate Limiting**: Built-in token bucket rate limiter (60 requests/minute)
- ⚡ **High Performance**: Optimized for millions of records with proper indexing
- 🔧 **Configurable Columns**: Dynamic column visibility and ordering
- 🌐 **CORS Support**: Cross-origin resource sharing enabled
- 📊 **SQLite Database**: Lightweight and portable database solution

## Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

## Quick Start

### 1. Generate SQLite Database

To initialize the database with tables and sample data, run:

```bash
python3 -c "from database import Database; db = Database(); db.seed_sample_data(); print('Database created successfully!')"
```

This command will:

- Create `hr_search.db` SQLite database file
- Initialize all required tables (companies, departments, positions, employees)
- Create performance indexes
- Populate the database with sample employee data

### 2. Start the Server

To start the API server, run:

```bash
# Start with default settings (localhost:8000), debug = false
python3 main.py

# Start with debug mode enabled (hot reload on file changes)
python3 main.py --debug=true

# Start on a specific port
python3 main.py --port=9000

# Start with debug mode and custom port
python3 main.py --debug=true --port=8080

# Start on all interfaces
python3 main.py --host=0.0.0.0 --port=8000
```

The server will display:

- API running message with the URL
- API Documentation link
- OpenAPI Spec link
- File watching status (if debug mode is enabled)

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

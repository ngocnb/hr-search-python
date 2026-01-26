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

### 1.1 Generate SQLite Database

To initialize the database with tables and sample data, run:

```bash
python3 -c 'from utils.database import Database; db = Database(); db.create_sample_data(); print("Database created successfully!")'
```

This command will:

- Create `hr_search.db` SQLite database file
- Initialize all required tables (companies, departments, positions, employees)
- Create performance indexes
- Populate the database with sample employee data

### 1.2 Create/Drop Full Text Search

To create the full text search indexes, run:

```bash
# Create full text search indexes
python3 utils/database_fts.py create
```

This commands will:

- **create**: Set up full text search (FTS5) virtual tables for optimized text searching

### 1.3 Seed Large Dataset (Optional - for Performance Testing)

To seed the database with 1 million employee records for performance testing, run:

```bash
# Seed with 1 million records (takes several minutes)
python3 utils/seed_large_dataset.py

# Seed with custom number of records
python3 utils/seed_large_dataset.py --records=500000

# Seed with 10 million records for larger-scale testing
python3 utils/seed_large_dataset.py --records=10000000
```

This script will:

- Generate realistic employee data (names, emails, locations, departments, positions)
- Insert records in optimized batches (10,000 records per batch)
- Display progress and performance metrics
- Show total database statistics when complete

**Note**: Seeding 1 million records typically takes 2-5 minutes depending on system performance.

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

## Docker

Build the image:

```bash
docker build -t hr-search .
```

Run the API (persist SQLite on your host):

```bash
docker run -p 8000:8000 -v $(pwd)/hr_search.db:/app/hr_search.db hr-search
```

Optional data prep inside the container:

- Seed sample data: `docker run --rm -v $(pwd)/hr_search.db:/app/hr_search.db hr-search python -c 'from utils.database import Database; Database().create_sample_data()'`
- Create FTS index: `docker run --rm -v $(pwd)/hr_search.db:/app/hr_search.db hr-search python utils/database_fts.py create`
- Seed large dataset: `docker run --rm -v $(pwd)/hr_search.db:/app/hr_search.db hr-search python utils/seed_large_dataset.py --records=1000000`

## Testing

### Test Structure

Tests are organized in the `tests/` folder with separate test files for different features:

- `tests/test_rate_limiter.py` - Tests for rate limiting functionality
- `tests/test_endpoints.py` - Tests for API endpoints
- `tests/test_headers.py` - Tests for HTTP headers and response formatting

### Run Unit Tests

To run the unit tests, use:

```bash
# Run all tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run all tests with verbose output
python3 -m unittest discover -s tests -p "test_*.py" -v

# Run specific test module
python3 -m unittest tests.test_rate_limiter

# Run specific test class
python3 -m unittest tests.test_rate_limiter.TestRateLimiter

# Run specific test method
python3 -m unittest tests.test_rate_limiter.TestRateLimiter.test_rate_limiter_allows_initial_requests

# Run endpoint tests only
python3 -m unittest tests.test_endpoints
```

### Test Coverage

The test suite includes:

- **Rate Limiter Tests** (`test_rate_limiter.py`): Token bucket algorithm, rate limiting per client, token refill mechanism
- **API Endpoint Tests** (`test_endpoints.py`): OpenAPI docs, OpenAPI spec, employee search, 404 errors, OPTIONS requests
- **HTTP Header Tests** (`test_headers.py`): CORS headers, content-type validation
- **Content-Type Tests**: Verify correct content types for different endpoints

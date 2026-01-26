"""
OpenAPI docs and spec helpers for the HR Employee Search API.
"""


def get_openapi_docs_html() -> str:
    """Return the static HTML docs page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Employee Search API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #fff; padding: 3px 8px; border-radius: 3px; font-weight: bold; background: green; }
            .get { background: #61affe; }
            .param { margin: 5px 0; }
            code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>HR Employee Search API</h1>
        <p>API documentation for the HR Employee Search Microservice</p>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/v1/employees/search</code>
            <h3>Search Employees</h3>
            <p>Send a JSON body with the filters below. All fields are optional.</p>
            <div class="param"><strong>q</strong>: Search text matched via FTS on first name, last name, email</div>
            <div class="param"><strong>company_ids</strong>: Array of company IDs (ints)</div>
            <div class="param"><strong>department_ids</strong>: Array of department IDs (ints)</div>
            <div class="param"><strong>position_ids</strong>: Array of position IDs (ints)</div>
            <div class="param"><strong>locations</strong>: Array of location substrings (strings)</div>
            <div class="param"><strong>statuses</strong>: Array of statuses (strings, e.g., Active, Not started, Terminated)</div>
            <div class="param"><strong>limit</strong>: Results per page (1-100, default 50)</div>
            <div class="param"><strong>page</strong>: Page number (>=1, default 1)</div>
            <p>Example body:</p>
<pre>{
  "q": "smith",
  "company_ids": [1],
  "department_ids": [2,3],
  "position_ids": [4],
  "locations": ["New York"],
  "statuses": ["Active", "Not started", "Terminated"],
  "limit": 25,
  "page": 1
}</pre>
        </div>
        
        <p><a href="/openapi.json">Download OpenAPI Spec</a></p>
    </body>
    </html>
    """


def get_openapi_spec() -> dict:
    """Return the OpenAPI spec dict."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "HR Employee Search API",
            "version": "1.0.0",
            "description": "API for searching employees in HR directory",
        },
        "paths": {
            "/api/v1/employees/search": {
                "post": {
                    "summary": "Search employees",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "q": {
                                            "type": "string",
                                            "description": "Full text search query applied to name and email",
                                        },
                                        "company_ids": {
                                            "type": "array",
                                            "items": {"type": "integer", "minimum": 1},
                                            "description": "List of company ids",
                                        },
                                        "department_ids": {
                                            "type": "array",
                                            "items": {"type": "integer", "minimum": 1},
                                            "description": "List of department ids",
                                        },
                                        "position_ids": {
                                            "type": "array",
                                            "items": {"type": "integer", "minimum": 1},
                                            "description": "List of position ids",
                                        },
                                        "locations": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Location substrings matched with LIKE",
                                        },
                                        "statuses": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Employment statuses (e.g., Active)",
                                        },
                                        "limit": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 100,
                                            "default": 50,
                                            "description": "Page size (1-100)",
                                        },
                                        "page": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "default": 1,
                                            "description": "Page number (>=1)",
                                        },
                                    },
                                },
                                "examples": {
                                    "basic": {
                                        "summary": "Search by text and company",
                                        "value": {
                                            "q": "smith",
                                            "company_ids": [1],
                                            "department_ids": [2, 3],
                                            "position_ids": [4],
                                            "locations": ["NY"],
                                            "statuses": ["Active"],
                                            "limit": 25,
                                            "page": 1,
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "employees": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "additionalProperties": True,
                                                },
                                            },
                                            "pagination": {
                                                "type": "object",
                                                "properties": {
                                                    "total": {"type": "integer"},
                                                    "limit": {"type": "integer"},
                                                    "offset": {"type": "integer"},
                                                    "has_more": {"type": "boolean"},
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "429": {"description": "Rate limit exceeded"},
                    },
                }
            }
        },
    }

# Dependency Audit Results

## Overview
This document summarizes the findings from a dependency audit of the project's requirements. The audit was conducted using `pipreqs` to analyze actual imports in the codebase and compare them with the declared dependencies in `requirements.txt`.

## Key Findings

1. **Unused Dependencies**: Several dependencies listed in `requirements.txt` appear to be unused in the codebase:
   - `aiosqlite` - No imports found
   - `redis` - No imports found
   - `duckdb` - No imports found
   - `celery` - No imports found
   - `numba` - No imports found
   - `sse-starlette` - Potentially unused, as the codebase seems to use `httpx-sse` instead

2. **Server vs. Client Dependencies**: The project includes both server and client components, but not all dependencies are required for both:
   - `fastapi`, `uvicorn`, and `starlette` are only used in server components
   - Many developers may only need the client components

3. **Actual Imports**: The `pipreqs` analysis identified the following key dependencies in actual use:
   - Web/API related: `aiohttp`, `httpx`, `fastapi`, `uvicorn`, `websockets`
   - Data processing: `numpy`, `faiss_cpu`
   - Database: `psycopg2`, `SQLAlchemy`, `pgvector`
   - Core utilities: `pydantic`, `PyYAML`, `python-dotenv`
   - Development: `pytest`, `setuptools`

## Recommendations

1. **Split Dependencies by Purpose**:
   - Core dependencies required for basic functionality
   - Optional dependencies for specific features
   - Server-specific dependencies
   - Development dependencies

2. **Use Optional Dependencies**: Leverage Python's optional dependency mechanism to allow users to install only what they need:
   ```
   pip install muxi[server]  # For server components
   pip install muxi[vector]  # For vector search capabilities
   ```

3. **Remove Unused Dependencies**: This will:
   - Speed up installation
   - Reduce potential security vulnerabilities
   - Minimize conflicts with other packages

4. **Consider Version Constraints**: Some version constraints are unnecessarily strict. Consider:
   - Using compatible release specifiers (`~=`) instead of strict minimums (`>=`)
   - Specifying upper bounds to prevent incompatible updates

## Implementation

An optimized `requirements.txt` file has been created as `requirements_optimized.txt`, which:

1. Organizes dependencies by purpose
2. Uses optional dependency groups
3. Removes unused packages
4. Maintains compatibility with existing code

To adopt this optimized approach:

```bash
# Install core requirements
pip install -r requirements_optimized.txt

# Install server components if needed
pip install -r requirements_optimized.txt[server]

# Install all optional components
pip install -r requirements_optimized.txt[optional]
```

**Note**: The format with sections like `[server]` and `[optional]` is for documentation purposes in the requirements file. For actual installation of optional dependencies, you would need to implement this in `setup.py` with the appropriate `extras_require` configuration.

## Next Steps

1. Verify that the optimized requirements file doesn't break functionality
2. Update `setup.py` to use the optimized dependency structure
3. Consider creating a smaller "client-only" installation option
4. Periodically re-run dependency analysis as the codebase evolves

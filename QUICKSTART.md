# ServiceLink - Quick Start Guide

## Prerequisites
- Python 3.8+
- pip

## Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Seed database with sample data**
   ```bash
   flask seed-db
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

## Sample Login Credentials

### Clients
- Username: `john_doe` | Password: `password123`
- Username: `jane_smith` | Password: `password123`

### Service Providers
- Username: `clean_pro` | Password: `password123`
- Username: `handy_helper` | Password: `password123`

## Running Tests

```bash
pytest
```

## Features to Explore

- **As a Client**: Search services, book time slots, leave reviews
- **As a Provider**: Add services, manage availability, view bookings
- **API**: Access `/api/services` for JSON data

## Project Structure

- `app/` - Main application code
- `tests/` - Unit tests
- `scripts/` - Utility scripts
- `config.py` - Configuration settings
- `run.py` - Application entry point

For detailed documentation, see README.md

# Country Currency & Exchange API

A RESTful API built with FastAPI that fetches country data from external APIs, stores it in a MySQL database, and provides CRUD operations with filtering, sorting, and image generation capabilities.

## Features

- **Data Fetching**: Automatically fetches countries and exchange rates from external APIs
- **Database Storage**: Stores country data with computed GDP estimates in MySQL
- **CRUD Operations**: Full create, read, update, delete operations
- **Filtering & Sorting**: Filter by region/currency and sort by various fields
- **Image Generation**: Creates summary images with statistics
- **Error Handling**: Comprehensive error handling with consistent JSON responses
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Requirements

- Python 3.10+
- MySQL 5.7+ or MySQL 8.0+
- pip (Python package installer)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/james-eo/countries-api.git
cd countries-api
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create a MySQL database and user:

```sql
CREATE DATABASE country_api;
CREATE USER 'api_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON country_api.* TO 'api_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Environment Configuration

Copy the `.env.example` file and update with your database credentials:

```bash
cp .env.exmpl .env.local or .env
```

Edit `.env.local or .env`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=api_user
DB_PASSWORD=your_password
DB_NAME=country_api

# External APIs (Optional - defaults provided)
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-secret-key-here (if needed)
```

### 6. Initialize Database

```bash
python create_db.py
```

### 7. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the built-in runner
python app/main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Core Endpoints

| Method   | Endpoint             | Description                                |
| -------- | -------------------- | ------------------------------------------ |
| `POST`   | `/countries/refresh` | Fetch and cache countries data             |
| `GET`    | `/countries`         | Get all countries (with filtering/sorting) |
| `GET`    | `/countries/{name}`  | Get specific country by name               |
| `DELETE` | `/countries/{name}`  | Delete a country record                    |
| `GET`    | `/status`            | Get API status and statistics              |
| `GET`    | `/countries/image`   | Get summary statistics image               |

### Utility Endpoints

| Method | Endpoint  | Description                   |
| ------ | --------- | ----------------------------- |
| `GET`  | `/`       | API information and endpoints |
| `GET`  | `/health` | Health check                  |

## Usage Examples

### 1. Refresh Countries Data

```bash
curl -X POST "http://localhost:8000/countries/refresh"
```

Response:

```json
{
  "message": "Countries data refreshed successfully",
  "countries_updated": 195,
  "countries_added": 55,
  "last_refreshed_at": "2025-10-26T18:00:00Z"
}
```

### 2. Get All Countries

```bash
curl "http://localhost:8000/countries"
```

### 3. Filter Countries by Region

```bash
curl "http://localhost:8000/countries?region=Africa"
```

### 4. Filter by Currency and Sort by GDP

```bash
curl "http://localhost:8000/countries?currency=USD&sort=gdp_desc"
```

### 5. Get Specific Country

```bash
curl "http://localhost:8000/countries/Nigeria"
```

### 6. Get API Status

```bash
curl "http://localhost:8000/status"
```

Response:

```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-26T18:00:00Z"
}
```

## Query Parameters

### GET /countries

| Parameter  | Type    | Description                 | Example          |
| ---------- | ------- | --------------------------- | ---------------- |
| `region`   | string  | Filter by region            | `?region=Africa` |
| `currency` | string  | Filter by currency code     | `?currency=NGN`  |
| `sort`     | string  | Sort by field               | `?sort=gdp_desc` |
| `skip`     | integer | Number of records to skip   | `?skip=0`        |
| `limit`    | integer | Number of records to return | `?limit=100`     |

### Sorting Options

- `gdp_desc` - By estimated GDP (descending)
- `gdp_asc` - By estimated GDP (ascending)
- `population_desc` - By population (descending)
- `population_asc` - By population (ascending)
- `name_asc` - By name (A-Z)
- `name_desc` - By name (Z-A)

## Error Responses

The API returns consistent JSON error responses:

### 400 Bad Request

```json
{
  "error": "Validation failed",
  "details": {
    "currency_code": "is required"
  }
}
```

### 404 Not Found

```json
{
  "error": "Country not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

### 503 Service Unavailable

```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from Countries API"
}
```

## Project Structure

```
country-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── country.py       # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── country.py       # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── countries_service.py  # External countries API
│   │   ├── exchange_service.py   # Exchange rates API
│   │   ├── country_service.py    # Business logic
│   │   └── image_service.py      # Image generation
│   ├── routers/
│   │   ├── __init__.py
│   │   └── countries.py     # API routes
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py    # Custom exceptions
├── cache/                   # Generated images storage
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── create_db.py            # Database initialization
├── .env                    # Environment variables
└── README.md              # This file
```

## Testing

### Manual Testing

1. **Start the server**:

   ```bash
   python app/main.py
   ```

2. **Test refresh endpoint**:

   ```bash
   curl -X POST "http://localhost:8000/countries/refresh"
   ```

3. **Test filtering**:

   ```bash
   curl "http://localhost:8000/countries?region=Africa&sort=gdp_desc"
   ```

4. **Test image generation**:
   ```bash
   curl "http://localhost:8000/countries/image" --output summary.png
   ```

### Database Verification

Connect to your MySQL database and verify data:

```sql
USE country_api;
SELECT COUNT(*) FROM countries;
SELECT name, currency_code, estimated_gdp FROM countries ORDER BY estimated_gdp DESC LIMIT 5;
```

## Deployment

### Environment Preparation

1. **Update environment variables** for production:

   ```env
   DEBUG=False
   DB_HOST=your-production-db-host
   SECRET_KEY=your-production-secret-key
   ```

2. **Database Migration**: Ensure your production database is set up and accessible.

### Platform Options

The API can be deployed on various platforms:

- **Railway**: `railway up`
- **Heroku**: Using `Procfile` with gunicorn
- **AWS**: EC2, ECS, or Lambda
- **DigitalOcean**: App Platform or Droplets

### Example Procfile (for Heroku-like platforms)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Configuration

### Database Connection

The application uses SQLAlchemy with MySQL. Connection pooling is enabled for better performance:

- **Pool Pre-ping**: Enabled to handle disconnections
- **Pool Recycle**: 300 seconds to prevent stale connections

### External APIs

- **Countries API**: `https://restcountries.com/v2/all`
- **Exchange Rates API**: `https://open.er-api.com/v6/latest/USD`
- **Timeout**: 30 seconds for all external requests

### Image Generation

- **Format**: PNG
- **Size**: 800x600 pixels
- **Storage**: Local file system in `cache/` directory
- **Font**: Liberation Sans (with fallback to default)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions:

- Check the API documentation at `/docs`
- Review error responses for debugging information
- Ensure all environment variables are properly configured

## Data Flow

1. **Refresh Process**:

   - Fetch countries from restcountries.com
   - Fetch exchange rates from open.er-api.com
   - Match currencies and calculate GDP
   - Update/insert records in database
   - Generate summary image

2. **Query Process**:

   - Receive API request
   - Apply filters and sorting
   - Return paginated results

3. **Error Handling**:
   - Validate input data
   - Handle external API failures
   - Return consistent error responses

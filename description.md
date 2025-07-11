# Habarovsk Forecast Buddy – Server Overview

## Purpose
REST API that helps forecast down-jacket sales in Khabarovsk, stores the results and allows working with historical data.


## Application Entry-point
```text
app/main.py
```
* Builds a FastAPI application (`app`).
* Adds CORS, request logging & custom error handlers.
* On startup checks:
  * Supabase REST API (database).
  * GigaChat service availability (AI model).
* Runs via `uvicorn app.main:app`.


## Exposed REST Endpoints  (`/api/v1` prefix)
| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET    | `/health`                      | Liveness/readiness probe |
| POST   | `/upload-csv`                 | Upload historical sales CSV |
| POST   | `/forecast`                   | Generate sales forecast for chosen SKU |
| GET    | `/data/{sku_id}`              | Get historical sales for SKU |
| GET    | `/forecast-history/{sku_id}`  | Get past forecasts for SKU |
| GET    | `/sku-list`                   | List all available SKU IDs |
| GET    | `/sample-csv`                 | Download CSV template |


## Core Services
### `csv_service.py`
* Detects & maps column names (flexible headers).
* Supports different delimiters, encodings, date formats.
* Returns validated `SalesDataRow` objects & collect errors.

### `supabase_client.py`
* Thin wrapper over Supabase **REST API** (not direct PG connection).
* CRUD for `sales_data` & `forecasts` tables.
* `ENVIRONMENT=test` ⇒ fully mocked responses for unit tests.

### `gigachat_service.py`
* Integrates with Sberbank’s **GigaChat** LLM.
* Builds Russian prompt with stats & trends.
* Obtains OAuth token or runs in `mock_mode` when creds absent.
* Parses JSON response (`predictions`, `explanation`, `confidence_scores`).

### `forecast_service.py`
Sequence:
1. Fetch historical data through Supabase.
2. Ask GigaChat (or mock) for forecast (7/14/30 days).
3. Convert answer → `ForecastResponse`; compute totals/averages.
4. Persist forecast to DB.
5. On failure issues simple fallback forecast.


## Data Schemas (`app/models/schemas.py`)
Pydantic models for:
* Health & error responses.
* CSV upload result, sales rows, forecast request/response.
* Enum `ForecastPeriod` (week, two weeks, month).


## Testing
Tests in `tests/` run in mocked mode (no external HTTP):
* Validate health, CSV parsing, forecast logic.


## Infrastructure & Dev
* `Dockerfile`, `start-dev.sh` – local run & containerization.
* SQL files for Supabase schema.
* Markdown guides (`SUPABASE_SETUP.md`, `GIGACHAT_SETUP.md`, etc.).
* `requirements.txt` defines Python deps (FastAPI, pandas, requests, python-dotenv …).

---
Developed under MIT licence. File generated automatically.

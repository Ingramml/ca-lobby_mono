# CA Lobby Monorepo Architecture

**Last Updated**: October 28, 2025
**Purpose**: Define the architecture and structure of the CA Lobby monorepo
**Audience**: Developers, architects, and contributors

---

## Overview

CA Lobby is a full-stack monorepo combining a Python data pipeline (backend) and React web application (frontend) for visualizing California lobbying disclosure data from CAL-ACCESS.

### Why Monorepo?

**Decision Rationale:**
- **Atomic commits** - Single commit updates backend + frontend + docs
- **Easier refactoring** - Change API contracts and frontend in one PR
- **Simplified coordination** - No version mismatch between components
- **Better code search** - Find all usages across the stack
- **Faster development** - Ideal for small teams (1-10 developers)

---

## Repository Structure

```
ca-lobby/                                # Monorepo root
│
├── backend/                             # Python data pipeline & database
│   ├── pipeline/                        # ETL scripts
│   │   ├── Bigquery_connection.py      # BigQuery client
│   │   ├── Bignewdownload_2.py         # Data download from BigLocalNews
│   │   ├── rowtypeforce.py             # Schema validation
│   │   ├── upload.py                   # Upload to BigQuery
│   │   └── upload_pipeline.py          # Complete ETL pipeline
│   │
│   ├── api/                             # Flask REST API (future)
│   │   ├── app.py                       # Flask application
│   │   ├── config.py                    # Configuration
│   │   ├── routes/                      # API endpoints
│   │   │   ├── organizations.py         # Organization queries
│   │   │   ├── lobbyists.py            # Lobbyist network queries
│   │   │   └── activity.py             # Activity timeline queries
│   │   └── models/                      # Data models
│   │       └── bigquery_client.py      # BigQuery wrapper
│   │
│   ├── CREATE_ALL_VIEWS.sql            # Complete view definitions (73 views)
│   ├── create_simple_views.sql         # Simplified view set
│   ├── SQL Queries/                     # Ad-hoc SQL queries
│   │
│   ├── docs/                            # Backend documentation
│   │   ├── California_Lobbying_Tables_Documentation.md
│   │   ├── BigQuery_Optimization_Plan.md
│   │   └── View_Architecture.md
│   │
│   ├── run_download.py                  # Pipeline runner: download
│   ├── run_upload_pipeline.py           # Pipeline runner: upload
│   ├── requirements.txt                 # Python dependencies
│   ├── .gitignore                       # Backend-specific ignores
│   └── README.md                        # Backend setup guide
│
├── frontend/                            # React web application
│   ├── src/                             # React source code
│   │   ├── components/                  # React components
│   │   │   ├── OrganizationProfile.js
│   │   │   ├── LobbyistNetwork.js
│   │   │   ├── ActivityTimeline.js
│   │   │   └── PaymentChart.js
│   │   ├── services/                    # API clients and data services
│   │   │   ├── api.js                   # Backend API client
│   │   │   └── dataService.js
│   │   ├── data/                        # Static data (temporary - dev only)
│   │   │   ├── payments.json
│   │   │   └── disclosures.json
│   │   ├── utils/                       # Utilities
│   │   └── App.js                       # Main application
│   │
│   ├── public/                          # Static assets
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── sample_data/                     # Development sample data
│   │   ├── v_payments_alameda.csv
│   │   └── v_filers_alameda.csv
│   │
│   ├── docs/                            # Frontend documentation
│   │   ├── Component_Guide.md
│   │   ├── Data_Flow.md
│   │   └── Deployment.md
│   │
│   ├── package.json                     # Node dependencies
│   ├── package-lock.json
│   ├── vercel.json                      # Deployment configuration
│   ├── .gitignore                       # Frontend-specific ignores
│   └── README.md                        # Frontend setup guide
│
├── docs/                                # Shared documentation
│   ├── ARCHITECTURE.md                  # This file
│   ├── DATABASE_STRATEGY_RECOMMENDATION.md
│   └── API_DOCUMENTATION.md             # API contract (future)
│
├── README.md                            # Project overview
├── .gitignore                           # Root-level ignores
└── docker-compose.yml                   # Local development environment
```

---

## System Architecture

### Current Architecture (Development Phase)

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Source                              │
│              BigLocalNews.org / CAL-ACCESS                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (1) Download CSV files
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend: Data Pipeline                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Download     │→ │ Type Force   │→ │ Upload to    │     │
│  │ (Bignew...)  │  │ (Schema)     │  │ BigQuery     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Google BigQuery                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Raw Tables (13 core tables)                     │       │
│  │  - CVR2_LOBBY_DISCLOSURE_CD                      │       │
│  │  - LPAY_CD (payments)                            │       │
│  │  - LEMP_CD (employer relationships)              │       │
│  │  - FILERS_CD (master registry)                   │       │
│  │  - ... and 9 more                                │       │
│  └──────────────────────────────────────────────────┘       │
│                         │                                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Views (73 views organized in 4 layers)          │       │
│  │  - Layer 1: Base views                           │       │
│  │  - Layer 2: Integration views                    │       │
│  │  - Layer 3: Analytical views                     │       │
│  │  - Layer 4: Filter views                         │       │
│  └──────────────────────────────────────────────────┘       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (2) Manual CSV export
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Sample Data (Alameda County only)               │
│  v_payments_alameda.csv, v_filers_alameda.csv               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (3) Python scripts convert to JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend: Static JSON Files                     │
│  src/data/payments.json, src/data/filers.json               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (4) React loads JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend: React Application                     │
│  Components render data from static files                    │
└─────────────────────────────────────────────────────────────┘
```

**Limitations:**
- ❌ Static data (no real-time updates)
- ❌ Alameda County only (~11 organizations)
- ❌ Missing data (NULL firm names, dates)
- ❌ No search/filter beyond pre-exported data

---

### Target Architecture (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                  Google BigQuery                             │
│  Raw Tables + Views (Full California Dataset)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (1) SQL queries
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend: Flask REST API                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │  API Endpoints:                                   │       │
│  │  GET /api/organizations?search=hospital          │       │
│  │  GET /api/organizations/:id                      │       │
│  │  GET /api/lobbyists/:id                          │       │
│  │  GET /api/activity/:id                           │       │
│  └──────────────────────────────────────────────────┘       │
│                                                               │
│  Features:                                                    │
│  - Parameterized queries (prevent SQL injection)             │
│  - Pagination (limit/offset)                                 │
│  - Caching (Redis or in-memory)                              │
│  - Rate limiting                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ (2) JSON responses
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend: React Application                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │  User enters search: "Alameda County"            │       │
│  │         ↓                                         │       │
│  │  API Client calls: /api/organizations?search=... │       │
│  │         ↓                                         │       │
│  │  Receives JSON with matching organizations       │       │
│  │         ↓                                         │       │
│  │  React components render results                 │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Real-time data (always current)
- ✅ Statewide coverage (~10,000+ organizations)
- ✅ Complete data (no NULL fields)
- ✅ Dynamic filtering (any search criteria)
- ✅ Scalable (handles millions of records)

---

## Data Flow

### ETL Pipeline (Backend)

1. **Download** - Fetch latest CAL-ACCESS data from BigLocalNews.org
   - Uses `bln-python-client` library
   - Downloads ZIP files containing CSV tables
   - Stores locally in `data/` (temporary, git-ignored)

2. **Type Enforcement** - Validate and transform data types
   - Reads schema from previous BigQuery tables
   - Ensures data types match (STRING, INTEGER, DATE, etc.)
   - Handles NULL values and missing data

3. **Upload** - Load data into BigQuery
   - Truncates existing tables (WRITE_TRUNCATE)
   - Uploads CSV data to BigQuery tables
   - Maintains schema consistency

4. **View Creation** - Create or update BigQuery views
   - Executes `CREATE_ALL_VIEWS.sql`
   - Defines 73 views across 4 layers
   - Optimizes query performance

### API Data Flow (Target)

1. **User Request** - Frontend sends HTTP request
   ```javascript
   GET /api/organizations?search=hospital&city=Oakland&limit=50
   ```

2. **Backend Processing** - Flask API validates and queries
   ```python
   # Validate input
   search = validate_input(request.args.get('search'))

   # Query BigQuery
   query = """
       SELECT * FROM v_org_profiles_complete
       WHERE organization_name LIKE @search
       AND organization_city = @city
       LIMIT @limit
   """
   results = bigquery_client.query(query, parameters=...)
   ```

3. **Response** - Return JSON to frontend
   ```json
   {
     "data": [
       {
         "organization_name": "Children's Hospital Oakland",
         "total_spent": 125000,
         "lobbyists": 3,
         "filings": 12
       }
     ],
     "count": 1,
     "limit": 50
   }
   ```

4. **Frontend Rendering** - React displays data
   ```javascript
   organizationData.map(org => (
     <OrganizationCard key={org.filer_id} data={org} />
   ))
   ```

---

## Technology Stack

### Backend

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Primary language | 3.9+ |
| **Google BigQuery** | Data warehouse | Cloud |
| **bln-python-client** | Data download | Latest |
| **pandas** | Data transformation | Latest |
| **Flask** | REST API (future) | 2.3+ |
| **google-cloud-bigquery** | BigQuery client | Latest |

### Frontend

| Technology | Purpose | Version |
|-----------|---------|---------|
| **React** | UI framework | 18.x |
| **JavaScript** | Primary language | ES6+ |
| **Recharts** | Data visualization | Latest |
| **Material-UI** | UI components | 5.x |
| **Vercel** | Hosting | Cloud |

### Infrastructure

| Service | Purpose | Cost |
|---------|---------|------|
| **BigQuery** | Data warehouse | ~$5-10/month |
| **Cloud Run** | API hosting (future) | ~$5-10/month |
| **Vercel** | Frontend hosting | Free tier |

---

## Development Workflow

### Local Development

1. **Clone the monorepo**
   ```bash
   git clone <repo-url>
   cd ca-lobby
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Configure credentials
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run locally**
   ```bash
   # Terminal 1: Backend (when API is ready)
   cd backend
   python api/app.py

   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

5. **Or use Docker**
   ```bash
   docker-compose up
   ```

### Making Changes

**Single-Stack Change (Backend OR Frontend):**
```bash
git checkout -b feature/add-search-filter

# Edit files in either backend/ or frontend/
# ...

git add .
git commit -m "feat: add search filter to organization list"
git push origin feature/add-search-filter
```

**Cross-Stack Change (Backend AND Frontend):**
```bash
git checkout -b feature/add-lobbyist-network

# Edit backend view
vim backend/create_lobbyist_network_view.sql

# Edit backend API
vim backend/api/routes/lobbyists.py

# Edit frontend component
vim frontend/src/components/LobbyistNetwork.js

# Edit shared docs
vim docs/API_DOCUMENTATION.md

# Commit everything together
git add .
git commit -m "feat: add lobbyist network feature

- Add v_lobbyist_network BigQuery view
- Add /api/lobbyists/:id endpoint
- Add LobbyistNetwork React component
- Update API documentation"

git push origin feature/add-lobbyist-network
```

**Benefits of Monorepo:**
- ✅ Single PR shows all changes
- ✅ No coordination between repos
- ✅ Changes are atomic (all or nothing)
- ✅ Documentation updates in same commit

---

## Deployment

### Backend Deployment

**Option 1: Cloud Run (Recommended)**
```bash
cd backend
gcloud run deploy ca-lobby-api \
  --source . \
  --region us-west1 \
  --allow-unauthenticated
```

**Option 2: App Engine**
```bash
cd backend
gcloud app deploy
```

### Frontend Deployment

**Vercel (Current):**
```bash
cd frontend
vercel deploy --prod
```

**Environment Variables:**
```
REACT_APP_API_URL=https://ca-lobby-api-xxx.run.app/api
```

---

## Security Considerations

### API Security (Future)

- **Authentication**: Consider API keys or OAuth for production
- **Rate Limiting**: Prevent abuse (e.g., 100 requests/minute)
- **Input Validation**: Sanitize all user inputs
- **Parameterized Queries**: Prevent SQL injection
- **CORS**: Configure allowed origins

### Data Privacy

- **Public Data**: All CAL-ACCESS data is public record
- **No PII**: No personal identifiable information beyond public disclosures
- **Aggregation**: Consider aggregating small payment amounts

---

## Performance Optimization

### Backend Optimization

1. **BigQuery Optimization** (See: backend/docs/BigQuery_Optimization_Plan.md)
   - Partitioning by date
   - Clustering by filer_id, entity_cd
   - Materialized views for common queries

2. **API Caching**
   - Cache organization profiles (10 min TTL)
   - Cache search results (5 min TTL)
   - Use Redis or in-memory cache

3. **Query Optimization**
   - Always use WHERE clauses
   - Limit result sets (pagination)
   - Avoid SELECT * (specify columns)

### Frontend Optimization

1. **Code Splitting**
   - Lazy load routes
   - Dynamic imports for large components

2. **Data Loading**
   - Pagination (load 50-100 records at a time)
   - Infinite scroll or "Load More" button
   - Loading states and skeletons

3. **Caching**
   - Cache API responses in React state/context
   - Use React Query or SWR for data fetching

---

## Testing Strategy

### Backend Testing

```bash
cd backend
pytest tests/
```

**Test Coverage:**
- Unit tests for data transformations
- Integration tests for BigQuery queries
- API endpoint tests (when API exists)

### Frontend Testing

```bash
cd frontend
npm test
```

**Test Coverage:**
- Component unit tests (Jest + React Testing Library)
- Integration tests for data flow
- End-to-end tests (Cypress)

---

## Maintenance

### Data Refresh

**Frequency:** Weekly (or as needed)

```bash
cd backend
python run_download.py    # Download latest CAL-ACCESS data
python run_upload_pipeline.py  # Upload to BigQuery
```

**Automation (Future):**
- Cron job or Cloud Scheduler
- GitHub Actions workflow
- Email notifications on success/failure

### View Updates

When schema changes:
```bash
cd backend
bq query --use_legacy_sql=false < CREATE_ALL_VIEWS.sql
```

---

## Contributing

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Code Review

All changes require:
- Clear commit messages
- Updated documentation
- Tests passing
- Code review approval

### Documentation

Keep documentation up to date:
- Update README.md when adding features
- Update ARCHITECTURE.md when changing structure
- Update API_DOCUMENTATION.md when modifying APIs
- Add inline code comments for complex logic

---

## Future Enhancements

### Short-term (3-6 months)

- [ ] Build Flask REST API
- [ ] Implement BigQuery optimization (partitioning, clustering)
- [ ] Add search and filter UI
- [ ] Deploy backend to Cloud Run

### Medium-term (6-12 months)

- [ ] Advanced visualizations (network graphs)
- [ ] Export functionality (PDF reports)
- [ ] User accounts and saved searches
- [ ] Email alerts for new filings

### Long-term (12+ months)

- [ ] Campaign contribution tracking
- [ ] Bill position tracking
- [ ] Comparative analysis tools
- [ ] Public API for researchers

---

## Support and Contact

For questions or issues:
- Review documentation in `docs/`
- Check backend README: `backend/README.md`
- Check frontend README: `frontend/README.md`

---

**Document Version:** 1.0
**Last Updated:** October 28, 2025
